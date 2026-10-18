from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from boxes.models import Box, Product, Order, OrderItem


class BoxAPITestCase(APITestCase):
    def setUp(self):
        self.box_sm = Box.objects.create(
            name="Small Mailer Box",
            code="BOX-API-SM",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("3.000"),
            cost=Decimal("1.50"),
            is_active=True
        )
        self.box_lg = Box.objects.create(
            name="Large Carton",
            code="BOX-API-LG",
            length=Decimal("50.00"),
            width=Decimal("40.00"),
            height=Decimal("30.00"),
            max_weight=Decimal("20.000"),
            cost=Decimal("5.00"),
            is_active=True
        )
        self.product = Product.objects.create(
            name="Keyboard",
            sku="SKU-KB-01",
            length=Decimal("40.00"),
            width=Decimal("12.00"),
            height=Decimal("4.00"),
            weight=Decimal("0.900")
        )
        self.order = Order.objects.create(
            order_number="ORD-API-001",
            customer_name="API User",
            status="PENDING"
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1
        )

    def test_get_boxes_list(self):
        url = reverse('boxes:api-box-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data['results']), 2)

    def test_get_products_list(self):
        url = reverse('boxes:api-product-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data['results']), 1)

    def test_recommend_box_api_adhoc_items(self):
        url = reverse('boxes:api-recommend-box')
        payload = {
            "items": [
                {
                    "name": "Headphones",
                    "length": 18.0,
                    "width": 12.0,
                    "height": 6.0,
                    "weight": 0.4,
                    "quantity": 1
                }
            ]
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['success'])
        self.assertEqual(resp.data['recommended_box']['code'], "BOX-API-SM")
        self.assertEqual(resp.data['status'], "OPTIMAL_FIT")
        self.assertIn("candidate_evaluations", resp.data)

    def test_recommend_box_api_by_order_id(self):
        url = reverse('boxes:api-recommend-box')
        payload = {"order_id": self.order.id}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['success'])
        # Keyboard length is 40cm, so it doesn't fit in Small Box (20x15x10). It fits in Large Box.
        self.assertEqual(resp.data['recommended_box']['code'], "BOX-API-LG")

    def test_recommend_box_api_invalid_payload(self):
        url = reverse('boxes:api-recommend-box')
        # Empty items list
        resp = self.client.post(url, {"items": []}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Negative dimension
        invalid_payload = {
            "items": [{"name": "Bad", "length": -5, "width": 10, "height": 10, "weight": 1}]
        }
        resp = self.client.post(url, invalid_payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_recommend_action(self):
        url = reverse('boxes:api-order-recommend', kwargs={'pk': self.order.id})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['success'])

        self.order.refresh_from_db()
        self.assertEqual(self.order.recommended_box, self.box_lg)

    def test_order_select_box_action(self):
        url = reverse('boxes:api-order-select-box', kwargs={'pk': self.order.id})
        payload = {"box_id": self.box_lg.id, "notes": "Packed by warehouse team A"}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        self.assertEqual(self.order.selected_box, self.box_lg)
        self.assertEqual(self.order.status, "PACKED")
        self.assertEqual(self.order.packing_notes, "Packed by warehouse team A")
