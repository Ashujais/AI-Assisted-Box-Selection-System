from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from boxes.models import Product, Box, Order, OrderItem, PackingLog


class ModelTestCase(TestCase):
    def setUp(self):
        self.box = Box.objects.create(
            name="Test Medium Box",
            code="BOX-TEST-MD",
            length=Decimal("30.00"),
            width=Decimal("20.00"),
            height=Decimal("15.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("2.50"),
            empty_weight=Decimal("0.200"),
            is_active=True
        )
        self.product1 = Product.objects.create(
            name="Test Book",
            sku="SKU-BOOK-01",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("4.00"),
            weight=Decimal("0.800"),
            description="A test programming book"
        )
        self.product2 = Product.objects.create(
            name="Test Mug",
            sku="SKU-MUG-01",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("0.350")
        )
        self.order = Order.objects.create(
            order_number="ORD-TEST-001",
            customer_name="Alice Smith",
            status="PENDING"
        )
        self.item1 = OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            quantity=2
        )
        self.item2 = OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            quantity=1
        )

    def test_product_properties(self):
        # 20 * 15 * 4 = 1200
        self.assertEqual(self.product1.volume, Decimal("1200.00"))
        self.assertEqual(
            self.product1.dimensions_sorted,
            (Decimal("4.00"), Decimal("15.00"), Decimal("20.00"))
        )
        self.assertIn("Test Book", str(self.product1))

    def test_box_properties(self):
        # 30 * 20 * 15 = 9000
        self.assertEqual(self.box.volume, Decimal("9000.00"))
        self.assertEqual(
            self.box.dimensions_sorted,
            (Decimal("15.00"), Decimal("20.00"), Decimal("30.00"))
        )
        self.assertIn("Test Medium Box", str(self.box))

    def test_order_properties(self):
        # Item 1: 2 * 0.8 = 1.6 kg
        # Item 2: 1 * 0.35 = 0.35 kg
        # Total: 1.95 kg
        self.assertEqual(self.order.total_weight, Decimal("1.950"))
        # Item 1 volume: 2 * 1200 = 2400
        # Item 2 volume: 1 * 1000 = 1000
        # Total: 3400
        self.assertEqual(self.order.total_volume, Decimal("3400.00"))
        self.assertEqual(self.order.total_quantity, 3)
        self.assertIn("ORD-TEST-001", str(self.order))

    def test_order_item_properties(self):
        self.assertEqual(self.item1.total_weight, Decimal("1.600"))
        self.assertEqual(self.item1.total_volume, Decimal("2400.00"))
        self.assertIn("Test Book", str(self.item1))

    def test_packing_log_creation(self):
        log = PackingLog.objects.create(
            order=self.order,
            recommended_box=self.box,
            success=True,
            volume_utilization_percent=37.78,
            weight_utilization_percent=39.00,
            evaluation_summary=[{"box_id": self.box.id, "fits": True}],
            placements=[{"name": "Test Book", "x": 0, "y": 0, "z": 0}],
            reason="Optimal box found"
        )
        self.assertTrue(log.success)
        self.assertEqual(log.order, self.order)
        self.assertIn("PackingLog", str(log))
