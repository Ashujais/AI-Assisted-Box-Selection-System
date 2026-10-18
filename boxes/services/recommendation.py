"""
Order Box Recommendation Service.
Orchestrates ORM querying, execution of PackingService, and persistence of PackingLog.
"""

from decimal import Decimal
from typing import Optional
from django.db import transaction

from boxes.models import Box, Order, OrderItem, PackingLog, Product
from boxes.services.packer import (
    PackingService,
    PackingResult,
    ItemToPack,
    BoxCandidate,
    model_to_box_candidate,
    order_to_items_to_pack,
)


class RecommendationService:
    """
    High-level business service to evaluate and recommend boxes for orders or item lists.
    """

    @classmethod
    def recommend_for_order(cls, order: Order, persist: bool = True) -> PackingResult:
        """
        Evaluate and recommend the optimal box for a database Order instance.
        If persist=True, updates order.recommended_box, box_fit_status, and saves a PackingLog.
        """
        items_to_pack = order_to_items_to_pack(order)
        active_boxes = [model_to_box_candidate(b) for b in Box.objects.filter(is_active=True)]

        result = PackingService.recommend_box(items_to_pack, active_boxes, allow_multi_box=True)

        if persist:
            with transaction.atomic():
                if result.recommended_box:
                    box_instance = Box.objects.get(id=result.recommended_box.id)
                    order.recommended_box = box_instance
                    order.box_fit_status = result.status
                else:
                    order.recommended_box = None
                    order.box_fit_status = result.status

                order.save(update_fields=['recommended_box', 'box_fit_status', 'updated_at'])

                # Log recommendation
                rec_box_obj = None
                if result.recommended_box:
                    rec_box_obj = Box.objects.get(id=result.recommended_box.id)

                PackingLog.objects.create(
                    order=order,
                    recommended_box=rec_box_obj,
                    success=result.success,
                    volume_utilization_percent=result.volume_utilization,
                    weight_utilization_percent=result.weight_utilization,
                    evaluation_summary=[c.to_dict() for c in result.candidate_evaluations],
                    placements=result.placements,
                    reason=result.message,
                )

        return result

    @classmethod
    def recommend_for_custom_items(
        cls,
        raw_items: list[dict],
        specific_box_ids: Optional[list[int]] = None
    ) -> PackingResult:
        """
        Ad-hoc recommendation for custom items provided via API or UI.
        raw_items is a list of dicts:
        [{
            'name': 'Item 1',
            'length': 20.0,
            'width': 15.0,
            'height': 10.0,
            'weight': 1.5,
            'quantity': 2,
            'sku': 'SKU-1' (optional)
        }, ...]
        """
        items_to_pack: list[ItemToPack] = []
        for idx, item in enumerate(raw_items):
            items_to_pack.append(ItemToPack(
                id=item.get('id', idx + 1),
                name=item.get('name', f"Item {idx + 1}"),
                sku=item.get('sku', f"CUSTOM-{idx + 1}"),
                length=float(item['length']),
                width=float(item['width']),
                height=float(item['height']),
                weight=float(item['weight']),
                quantity=int(item.get('quantity', 1)),
            ))

        boxes_qs = Box.objects.filter(is_active=True)
        if specific_box_ids:
            boxes_qs = boxes_qs.filter(id__in=specific_box_ids)

        active_boxes = [model_to_box_candidate(b) for b in boxes_qs]

        result = PackingService.recommend_box(items_to_pack, active_boxes, allow_multi_box=True)
        return result
