from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from boxes.models import Box, Product, Order, OrderItem


class WebViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.box = Box.objects.create(
            name="UI Test Box",
            code="BOX-UI-01",
            length=Decimal("30.00"),
            width=Decimal("20.00"),
            height=Decimal("15.00"),
            max_weight=Decimal("5.000"),
            cost=Decimal("2.50"),
            is_active=True
        )
        self.product = Product.objects.create(
            name="UI Product",
            sku="SKU-UI-01",
            length=Decimal("15.00"),
            width=Decimal("10.00"),
            height=Decimal("5.00"),
            weight=Decimal("0.500")
        )
        self.order = Order.objects.create(
            order_number="ORD-UI-001",
            customer_name="UI Customer",
            status="PENDING"
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1
        )

    def test_dashboard_view(self):
        url = reverse('boxes:dashboard')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Warehouse Packaging Dashboard")
        self.assertIn('total_boxes', resp.context)
        self.assertIn('pending_orders', resp.context)

    def test_order_list_view(self):
        url = reverse('boxes:order_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "ORD-UI-001")

        # Test filter by status
        resp_filtered = self.client.get(url, {'status': 'PENDING'})
        self.assertEqual(resp_filtered.status_code, 200)
        self.assertContains(resp_filtered, "ORD-UI-001")

    def test_order_detail_view_get(self):
        url = reverse('boxes:order_detail', kwargs={'pk': self.order.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Order Packaging Station")
        self.assertContains(resp, "ORD-UI-001")
        self.assertIn('recommendation', resp.context)

    def test_order_detail_view_post_run_recommendation(self):
        url = reverse('boxes:order_detail', kwargs={'pk': self.order.pk})
        resp = self.client.post(url, {'action': 'run_recommendation'})
        self.assertEqual(resp.status_code, 302)  # Redirects after POST
        self.order.refresh_from_db()
        self.assertEqual(self.order.recommended_box, self.box)

    def test_order_detail_view_post_select_box(self):
        url = reverse('boxes:order_detail', kwargs={'pk': self.order.pk})
        resp = self.client.post(url, {
            'action': 'select_box',
            'box_id': self.box.id,
            'notes': 'Manual warehouse confirmation'
        })
        self.assertEqual(resp.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.selected_box, self.box)
        self.assertEqual(self.order.status, 'PACKED')

    def test_interactive_recommender_view(self):
        url = reverse('boxes:recommender')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Interactive Box Recommender Sandbox")

    def test_box_list_view(self):
        url = reverse('boxes:box_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "BOX-UI-01")

    def test_product_list_view(self):
        url = reverse('boxes:product_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "UI Product")
