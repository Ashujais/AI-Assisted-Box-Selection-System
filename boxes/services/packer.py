"""
3D Bin Packing and Box Selection Service.

Provides:
- 3D spatial packing simulation with 6-degrees-of-freedom rotations
- First-Fit Decreasing (FFD) heuristic with coordinate placement
- Multi-criteria box selection (cost minimization, volume utilization, weight capacity)
- Detailed diagnostic feedback on rejected boxes
- Multi-box shipment splitting fallback
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Optional


@dataclass
class ItemToPack:
    """Represents a product item or collection of items to be packed."""
    id: Any
    name: str
    length: float
    width: float
    height: float
    weight: float
    quantity: int = 1
    sku: str = ""

    @property
    def unit_volume(self) -> float:
        return self.length * self.width * self.height

    @property
    def total_volume(self) -> float:
        return self.unit_volume * self.quantity

    @property
    def total_weight(self) -> float:
        return self.weight * self.quantity

    @property
    def dimensions_sorted(self) -> tuple[float, float, float]:
        return tuple(sorted([self.length, self.width, self.height]))


@dataclass
class BoxCandidate:
    """Represents a shipping box candidate."""
    id: Any
    name: str
    code: str
    length: float
    width: float
    height: float
    max_weight: float
    cost: float
    empty_weight: float = 0.0
    is_active: bool = True

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height

    @property
    def dimensions_sorted(self) -> tuple[float, float, float]:
        return tuple(sorted([self.length, self.width, self.height]))


@dataclass
class PlacedItem:
    """Record of an item placed inside a 3D box."""
    item_id: Any
    name: str
    sku: str
    x: float
    y: float
    z: float
    dx: float  # length along X
    dy: float  # width along Y
    dz: float  # height along Z
    weight: float

    def to_dict(self) -> dict:
        return {
            'item_id': self.item_id,
            'name': self.name,
            'sku': self.sku,
            'x': round(self.x, 2),
            'y': round(self.y, 2),
            'z': round(self.z, 2),
            'dx': round(self.dx, 2),
            'dy': round(self.dy, 2),
            'dz': round(self.dz, 2),
            'weight': round(self.weight, 3),
        }


@dataclass
class CandidateEvaluation:
    """Evaluation result for a specific box candidate."""
    box_id: Any
    box_name: str
    box_code: str
    box_cost: float
    box_volume: float
    box_max_weight: float
    fits: bool
    rejection_reason: Optional[str] = None
    volume_utilization: float = 0.0
    weight_utilization: float = 0.0
    placements: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'box_id': self.box_id,
            'box_name': self.box_name,
            'box_code': self.box_code,
            'box_cost': round(self.box_cost, 2),
            'box_volume': round(self.box_volume, 2),
            'box_max_weight': round(self.box_max_weight, 3),
            'fits': self.fits,
            'rejection_reason': self.rejection_reason,
            'volume_utilization': round(self.volume_utilization, 2),
            'weight_utilization': round(self.weight_utilization, 2),
            'placements_count': len(self.placements),
        }


@dataclass
class MultiBoxPackage:
    """Represents one box in a multi-box shipment plan."""
    box: BoxCandidate
    items: list[dict]
    total_weight: float
    total_volume: float
    cost: float
    volume_utilization: float


@dataclass
class PackingResult:
    """Final output from the Box Selection recommendation engine."""
    success: bool
    recommended_box: Optional[BoxCandidate] = None
    status: str = 'NOT_EVALUATED'  # OPTIMAL_FIT, ALTERNATIVE_FIT, MULTI_BOX_NEEDED, NO_FIT
    total_order_weight: float = 0.0
    total_order_volume: float = 0.0
    total_items_count: int = 0
    volume_utilization: float = 0.0
    weight_utilization: float = 0.0
    placements: list[dict] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)
    candidate_evaluations: list[CandidateEvaluation] = field(default_factory=list)
    alternative_boxes: list[CandidateEvaluation] = field(default_factory=list)
    multi_box_packages: list[MultiBoxPackage] = field(default_factory=list)
    multi_box_total_cost: float = 0.0
    message: str = ""

    def to_dict(self) -> dict:
        return {
            'success': self.success,
            'status': self.status,
            'message': self.message,
            'recommended_box': {
                'id': self.recommended_box.id,
                'name': self.recommended_box.name,
                'code': self.recommended_box.code,
                'cost': round(self.recommended_box.cost, 2),
                'length': round(self.recommended_box.length, 2),
                'width': round(self.recommended_box.width, 2),
                'height': round(self.recommended_box.height, 2),
                'volume': round(self.recommended_box.volume, 2),
                'max_weight': round(self.recommended_box.max_weight, 3),
            } if self.recommended_box else None,
            'metrics': {
                'total_order_weight_kg': round(self.total_order_weight, 3),
                'total_order_volume_cm3': round(self.total_order_volume, 2),
                'total_items_count': self.total_items_count,
                'volume_utilization_percent': round(self.volume_utilization, 2),
                'weight_utilization_percent': round(self.weight_utilization, 2),
            },
            'placements': self.placements,
            'candidate_evaluations': [c.to_dict() for c in self.candidate_evaluations],
            'alternative_boxes': [a.to_dict() for a in self.alternative_boxes],
            'multi_box_plan': [
                {
                    'box_name': p.box.name,
                    'box_code': p.box.code,
                    'cost': round(p.cost, 2),
                    'total_weight_kg': round(p.total_weight, 3),
                    'volume_utilization_percent': round(p.volume_utilization, 2),
                    'items': p.items,
                }
                for p in self.multi_box_packages
            ] if self.multi_box_packages else [],
            'multi_box_total_cost': round(self.multi_box_total_cost, 2) if self.multi_box_packages else 0.0,
        }


class PackingService:
    """
    Core engine for 3D box packing simulation and box recommendation.
    """

    @staticmethod
    def get_rotations(length: float, width: float, height: float) -> list[tuple[float, float, float]]:
        """
        Generate all unique 3D orientations (permutations of length, width, height)
        for a rectangular cuboid.
        """
        orientations = {
            (length, width, height),
            (length, height, width),
            (width, length, height),
            (width, height, length),
            (height, length, width),
            (height, width, length),
        }
        return list(orientations)

    @staticmethod
    def _is_overlap(p1: PlacedItem, x: float, y: float, z: float, dx: float, dy: float, dz: float) -> bool:
        """
        Check if item bounding box at (x, y, z) with size (dx, dy, dz)
        overlaps with already placed item p1.
        Uses standard 3D Axis-Aligned Bounding Box (AABB) intersection check.
        """
        overlap_x = max(p1.x, x) < min(p1.x + p1.dx, x + dx)
        overlap_y = max(p1.y, y) < min(p1.y + p1.dy, y + dy)
        overlap_z = max(p1.z, z) < min(p1.z + p1.dz, z + dz)
        return overlap_x and overlap_y and overlap_z

    @classmethod
    def simulate_3d_packing(
        cls,
        box: BoxCandidate,
        individual_items: list[dict]
    ) -> tuple[bool, list[PlacedItem], Optional[str]]:
        """
        Simulate 3D physical placement of items inside a box using
        First-Fit Decreasing with 6-DOF Rotations and Candidate Point Placement.

        Returns:
            (success: bool, placements: list[PlacedItem], failure_reason: Optional[str])
        """
        placed_items: list[PlacedItem] = []

        # Candidate placement points in 3D space: (x, y, z)
        # We start at the bottom-back-left corner (0, 0, 0)
        candidate_points: list[tuple[float, float, float]] = [(0.0, 0.0, 0.0)]

        # Sort individual items using First-Fit Decreasing heuristic:
        # Largest volume first, then largest dimension first
        sorted_items = sorted(
            individual_items,
            key=lambda it: (it['length'] * it['width'] * it['height'], max(it['length'], it['width'], it['height'])),
            reverse=True
        )

        for item in sorted_items:
            placed = False
            l, w, h = item['length'], item['width'], item['height']
            rotations = cls.get_rotations(l, w, h)

            # Sort candidate points to encourage tight, stable packing:
            # 1. lowest Z (bottom-up packing)
            # 2. lowest Y
            # 3. lowest X
            candidate_points.sort(key=lambda pt: (pt[2], pt[1], pt[0]))

            for pt in candidate_points:
                px, py, pz = pt

                for dx, dy, dz in rotations:
                    # Boundary check against box internal dimensions
                    if px + dx > box.length + 1e-6:
                        continue
                    if py + dy > box.width + 1e-6:
                        continue
                    if pz + dz > box.height + 1e-6:
                        continue

                    # Overlap collision check against all already placed items
                    has_collision = False
                    for existing in placed_items:
                        if cls._is_overlap(existing, px, py, pz, dx, dy, dz):
                            has_collision = True
                            break

                    if not has_collision:
                        # Successful placement found!
                        new_placed = PlacedItem(
                            item_id=item['id'],
                            name=item['name'],
                            sku=item.get('sku', ''),
                            x=px,
                            y=py,
                            z=pz,
                            dx=dx,
                            dy=dy,
                            dz=dz,
                            weight=item['weight'],
                        )
                        placed_items.append(new_placed)
                        placed = True

                        # Generate new candidate points from the vertices of the newly placed box
                        new_points = [
                            (px + dx, py, pz),
                            (px, py + dy, pz),
                            (px, py, pz + dz),
                        ]

                        for npt in new_points:
                            nx, ny, nz = npt
                            # Only add if inside box boundaries and not duplicate
                            if nx <= box.length and ny <= box.width and nz <= box.height:
                                # Also check if candidate point is inside any existing placed box
                                point_enclosed = False
                                for ex in placed_items:
                                    if (ex.x <= nx < ex.x + ex.dx and
                                        ex.y <= ny < ex.y + ex.dy and
                                        ex.z <= nz < ex.z + ex.dz):
                                        point_enclosed = True
                                        break
                                if not point_enclosed and npt not in candidate_points:
                                    candidate_points.append(npt)

                        break  # Break out of rotations loop

                if placed:
                    break  # Break out of candidate points loop

            if not placed:
                reason = (
                    f"Item '{item['name']}' ({l:.1f}x{w:.1f}x{h:.1f}cm) could not fit spatially "
                    f"in box '{box.name}' ({box.length}x{box.width}x{box.height}cm) without overlapping."
                )
                return False, [], reason

        return True, placed_items, None

    @classmethod
    def evaluate_box(
        cls,
        box: BoxCandidate,
        items: list[ItemToPack]
    ) -> CandidateEvaluation:
        """
        Evaluate if a candidate box can accommodate all items in the order,
        checking:
        1. Total weight <= box.max_weight
        2. Total item volume <= box.volume
        3. Individual item dimensions <= box dimensions (in at least one rotation)
        4. 3D spatial simulation fit
        """
        total_weight = sum(item.total_weight for item in items)
        total_volume = sum(item.total_volume for item in items)
        effective_weight = total_weight + box.empty_weight

        # 1. Weight capacity check
        if effective_weight > box.max_weight + 1e-6:
            return CandidateEvaluation(
                box_id=box.id,
                box_name=box.name,
                box_code=box.code,
                box_cost=box.cost,
                box_volume=box.volume,
                box_max_weight=box.max_weight,
                fits=False,
                rejection_reason=(
                    f"Total weight ({effective_weight:.2f} kg) exceeds box capacity ({box.max_weight:.2f} kg)"
                )
            )

        # 2. Volume capacity check
        if total_volume > box.volume + 1e-6:
            return CandidateEvaluation(
                box_id=box.id,
                box_name=box.name,
                box_code=box.code,
                box_cost=box.cost,
                box_volume=box.volume,
                box_max_weight=box.max_weight,
                fits=False,
                rejection_reason=(
                    f"Total item volume ({total_volume:.1f} cm³) exceeds box volume ({box.volume:.1f} cm³)"
                )
            )

        # 3. Individual dimensions check (fast filter before 3D packing)
        box_sorted = box.dimensions_sorted
        for item in items:
            item_sorted = item.dimensions_sorted
            if (item_sorted[0] > box_sorted[0] + 1e-6 or
                item_sorted[1] > box_sorted[1] + 1e-6 or
                item_sorted[2] > box_sorted[2] + 1e-6):
                return CandidateEvaluation(
                    box_id=box.id,
                    box_name=box.name,
                    box_code=box.code,
                    box_cost=box.cost,
                    box_volume=box.volume,
                    box_max_weight=box.max_weight,
                    fits=False,
                    rejection_reason=(
                        f"Item '{item.name}' ({item.length}x{item.width}x{item.height}cm) "
                        f"exceeds box boundaries ({box.length}x{box.width}x{box.height}cm)"
                    )
                )

        # 4. Expand items into individual units for 3D placement simulation
        individual_units: list[dict] = []
        for item in items:
            for i in range(item.quantity):
                individual_units.append({
                    'id': f"{item.id}_{i+1}" if item.quantity > 1 else str(item.id),
                    'name': item.name,
                    'sku': item.sku,
                    'length': item.length,
                    'width': item.width,
                    'height': item.height,
                    'weight': item.weight,
                })

        # Run 3D placement simulation
        success, placements, fail_reason = cls.simulate_3d_packing(box, individual_units)
        if not success:
            return CandidateEvaluation(
                box_id=box.id,
                box_name=box.name,
                box_code=box.code,
                box_cost=box.cost,
                box_volume=box.volume,
                box_max_weight=box.max_weight,
                fits=False,
                rejection_reason=fail_reason
            )

        # If fits, compute utilization metrics
        vol_util = (total_volume / box.volume) * 100.0 if box.volume > 0 else 0.0
        wt_util = (effective_weight / box.max_weight) * 100.0 if box.max_weight > 0 else 0.0

        return CandidateEvaluation(
            box_id=box.id,
            box_name=box.name,
            box_code=box.code,
            box_cost=box.cost,
            box_volume=box.volume,
            box_max_weight=box.max_weight,
            fits=True,
            volume_utilization=vol_util,
            weight_utilization=wt_util,
            placements=[p.to_dict() for p in placements]
        )

    @classmethod
    def recommend_box(
        cls,
        items: list[ItemToPack],
        boxes: list[BoxCandidate],
        allow_multi_box: bool = True
    ) -> PackingResult:
        """
        Main recommendation entrypoint:
        Evaluates candidate boxes and selects the optimal box.

        Optimization Criteria:
        1. Minimal Cost (primary objective)
        2. Minimal Volume / Empty space (secondary tie-breaker)
        3. Highest Volume Utilization (tertiary tie-breaker)

        If no single box fits:
        Calculates a multi-box shipment plan if enabled.
        """
        total_order_weight = sum(item.total_weight for item in items)
        total_order_volume = sum(item.total_volume for item in items)
        total_items_count = sum(item.quantity for item in items)

        if not items or total_items_count == 0:
            return PackingResult(
                success=False,
                status='NO_FIT',
                message="Order contains no items to pack.",
                candidate_evaluations=[]
            )

        active_boxes = [b for b in boxes if b.is_active]
        if not active_boxes:
            return PackingResult(
                success=False,
                status='NO_FIT',
                message="No active shipping boxes available in the warehouse.",
                total_order_weight=total_order_weight,
                total_order_volume=total_order_volume,
                total_items_count=total_items_count,
            )

        evaluations: list[CandidateEvaluation] = []
        eligible_evaluations: list[CandidateEvaluation] = []

        for box in active_boxes:
            eval_res = cls.evaluate_box(box, items)
            evaluations.append(eval_res)
            if eval_res.fits:
                eligible_evaluations.append(eval_res)

        # Sort all evaluations by cost ascending
        evaluations.sort(key=lambda e: (e.box_cost, e.box_volume))

        if eligible_evaluations:
            # Sort eligible boxes:
            # 1. Cost ascending (cheapest box)
            # 2. Volume ascending (smallest box among equal cost)
            # 3. Volume utilization descending (tightest fit)
            eligible_evaluations.sort(
                key=lambda e: (e.box_cost, e.box_volume, -e.volume_utilization)
            )

            best_eval = eligible_evaluations[0]
            recommended_box = next(b for b in active_boxes if b.id == best_eval.box_id)

            alternatives = eligible_evaluations[1:]

            status = 'OPTIMAL_FIT'
            msg = f"Optimal box found: '{best_eval.box_name}' (Cost: ${best_eval.box_cost:.2f}, Volume utilization: {best_eval.volume_utilization:.1f}%)."

            return PackingResult(
                success=True,
                recommended_box=recommended_box,
                status=status,
                total_order_weight=total_order_weight,
                total_order_volume=total_order_volume,
                total_items_count=total_items_count,
                volume_utilization=best_eval.volume_utilization,
                weight_utilization=best_eval.weight_utilization,
                placements=best_eval.placements,
                candidate_evaluations=evaluations,
                alternative_boxes=alternatives,
                message=msg,
            )

        # No single box fits:
        rejections = [
            f"Box '{e.box_name}' ({e.box_code}): {e.rejection_reason}"
            for e in evaluations if not e.fits
        ]

        multi_box_packages: list[MultiBoxPackage] = []
        multi_box_cost = 0.0

        if allow_multi_box and len(items) > 0:
            multi_box_packages, multi_box_cost = cls._plan_multi_box(items, active_boxes)

        if multi_box_packages:
            msg = (
                f"No single box can fit all items. Recommended multi-box shipment plan "
                f"using {len(multi_box_packages)} box(es) with total estimated cost of ${multi_box_cost:.2f}."
            )
            return PackingResult(
                success=True,
                recommended_box=None,
                status='MULTI_BOX_NEEDED',
                total_order_weight=total_order_weight,
                total_order_volume=total_order_volume,
                total_items_count=total_items_count,
                rejection_reasons=rejections,
                candidate_evaluations=evaluations,
                multi_box_packages=multi_box_packages,
                multi_box_total_cost=multi_box_cost,
                message=msg,
            )

        # Absolute no fit (e.g. single item too large for any box)
        return PackingResult(
            success=False,
            recommended_box=None,
            status='NO_FIT',
            total_order_weight=total_order_weight,
            total_order_volume=total_order_volume,
            total_items_count=total_items_count,
            rejection_reasons=rejections,
            candidate_evaluations=evaluations,
            message="No suitable shipping box could be found for this order. Items exceed warehouse packaging capacities.",
        )

    @classmethod
    def _plan_multi_box(
        cls,
        items: list[ItemToPack],
        boxes: list[BoxCandidate]
    ) -> tuple[list[MultiBoxPackage], float]:
        """
        Greedy multi-box packing fallback:
        Splits items into multiple boxes when no single box is sufficient.
        """
        # Expand items to individual units
        unpacked_units: list[dict] = []
        for item in items:
            for i in range(item.quantity):
                unpacked_units.append({
                    'id': f"{item.id}_{i+1}" if item.quantity > 1 else str(item.id),
                    'name': item.name,
                    'sku': item.sku,
                    'length': item.length,
                    'width': item.width,
                    'height': item.height,
                    'weight': item.weight,
                })

        # Sort boxes by cost ascending
        sorted_boxes = sorted(boxes, key=lambda b: (b.cost, b.volume))

        # Sort unpacked units by volume descending
        unpacked_units.sort(
            key=lambda u: (u['length'] * u['width'] * u['height'], max(u['length'], u['width'], u['height'])),
            reverse=True
        )

        packages: list[MultiBoxPackage] = []
        total_cost = 0.0

        while unpacked_units:
            best_package_box: Optional[BoxCandidate] = None
            best_packed_items: list[dict] = []
            best_cost_per_item = float('inf')

            for box in sorted_boxes:
                # Try to pack as many remaining units as possible into this box
                packed_in_box: list[dict] = []
                current_units: list[dict] = []

                for unit in unpacked_units:
                    # Check if adding this unit still fits
                    test_units = current_units + [unit]
                    test_items = [
                        ItemToPack(
                            id=u['id'],
                            name=u['name'],
                            sku=u['sku'],
                            length=u['length'],
                            width=u['width'],
                            height=u['height'],
                            weight=u['weight'],
                            quantity=1,
                        )
                        for u in test_units
                    ]
                    eval_res = cls.evaluate_box(box, test_items)
                    if eval_res.fits:
                        current_units = test_units
                        packed_in_box.append(unit)

                if packed_in_box:
                    cost_per_item = box.cost / len(packed_in_box)
                    if cost_per_item < best_cost_per_item or (
                        cost_per_item == best_cost_per_item and len(packed_in_box) > len(best_packed_items)
                    ):
                        best_cost_per_item = cost_per_item
                        best_package_box = box
                        best_packed_items = packed_in_box

            if not best_package_box or not best_packed_items:
                # Could not pack any remaining unit into any box!
                return [], 0.0

            # Remove packed items from unpacked list
            for p_item in best_packed_items:
                unpacked_units.remove(p_item)

            pkg_weight = sum(u['weight'] for u in best_packed_items)
            pkg_vol = sum(u['length'] * u['width'] * u['height'] for u in best_packed_items)
            vol_util = (pkg_vol / best_package_box.volume) * 100.0 if best_package_box.volume > 0 else 0.0

            packages.append(MultiBoxPackage(
                box=best_package_box,
                items=best_packed_items,
                total_weight=pkg_weight,
                total_volume=pkg_vol,
                cost=best_package_box.cost,
                volume_utilization=vol_util
            ))
            total_cost += best_package_box.cost

        return packages, total_cost


# Helper functions to convert between Django ORM models and Service Dataclasses

def model_to_box_candidate(box_model) -> BoxCandidate:
    """Convert Django Box model instance to BoxCandidate dataclass."""
    return BoxCandidate(
        id=box_model.id,
        name=box_model.name,
        code=box_model.code,
        length=float(box_model.length),
        width=float(box_model.width),
        height=float(box_model.height),
        max_weight=float(box_model.max_weight),
        cost=float(box_model.cost),
        empty_weight=float(box_model.empty_weight),
        is_active=box_model.is_active,
    )


def order_to_items_to_pack(order_model) -> list[ItemToPack]:
    """Convert Django Order model's items to list of ItemToPack dataclasses."""
    items: list[ItemToPack] = []
    for item in order_model.items.select_related('product').all():
        p = item.product
        items.append(ItemToPack(
            id=p.id,
            name=p.name,
            sku=p.sku,
            length=float(p.length),
            width=float(p.width),
            height=float(p.height),
            weight=float(p.weight),
            quantity=item.quantity,
        ))
    return items
