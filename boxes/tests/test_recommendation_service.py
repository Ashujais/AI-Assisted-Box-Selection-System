from decimal import Decimal
from django.test import TestCase
from boxes.models import Box, Product, Order, OrderItem, PackingLog
from boxes.services.recommendation import RecommendationService


class RecommendationServiceTestCase(TestCase):
    def setUp(self):
        self.box_sm = Box.objects.create(
            name="Small Mailer",
            code="BOX-SM",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("3.000"),
            cost=Decimal("1.50"),
            is_active=True
        )
        self.box_lg = Box.objects.create(
            name="Large Carton",
            code="BOX-LG",
            length=Decimal("50.00"),
            width=Decimal("40.00"),
            height=Decimal("30.00"),
            max_weight=Decimal("20.000"),
            cost=Decimal("5.00"),
            is_active=True
        )
        self.product_mug = Product.objects.create(
            name="Coffee Mug",
            sku="MUG-01",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.400")
        )
        self.order = Order.objects.create(
            order_number="ORD-REC-01",
            customer_name="Bob Test",
            status="PENDING"
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product_mug,
            quantity=2
        )

    def test_recommend_for_order_persists_log_and_box(self):
        result = RecommendationService.recommend_for_order(self.order, persist=True)

        self.assertTrue(result.success)
        self.assertEqual(result.recommended_box.id, self.box_sm.id)

        # Refresh order from DB
        self.order.refresh_from_db()
        self.assertEqual(self.order.recommended_box, self.box_sm)
        self.assertEqual(self.order.box_fit_status, "OPTIMAL_FIT")

        # Verify PackingLog was created
        log = PackingLog.objects.filter(order=self.order).first()
        self.assertIsNotNone(log)
        self.assertTrue(log.success)
        self.assertEqual(log.recommended_box, self.box_sm)
        self.assertGreater(log.volume_utilization_percent, 0.0)

    def test_recommend_for_custom_items(self):
        raw_items = [
            {
                "name": "Custom Widget",
                "length": 15.0,
                "width": 10.0,
                "height": 5.0,
                "weight": 0.5,
                "quantity": 1
            }
        ]
        result = RecommendationService.recommend_for_custom_items(raw_items)
        self.assertTrue(result.success)
        self.assertEqual(result.recommended_box.id, self.box_sm.id)
