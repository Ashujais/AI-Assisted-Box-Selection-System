from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from boxes.models import Product, Box, Order, OrderItem
from boxes.services.recommendation import RecommendationService


class Command(BaseCommand):
    help = "Seeds database with realistic ecommerce products, shipping boxes, and sample orders."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding ecommerce boxes, products, and orders..."))

        with transaction.atomic():
            # 1. Seed Shipping Boxes
            boxes_data = [
                {
                    'name': 'Small Mailer Box',
                    'code': 'BOX-SM-01',
                    'length': Decimal('22.00'),
                    'width': Decimal('16.00'),
                    'height': Decimal('10.00'),
                    'max_weight': Decimal('2.500'),
                    'cost': Decimal('1.50'),
                    'empty_weight': Decimal('0.120'),
                    'is_active': True,
                },
                {
                    'name': 'Standard Book & Media Box',
                    'code': 'BOX-MD-01',
                    'length': Decimal('32.00'),
                    'width': Decimal('24.00'),
                    'height': Decimal('14.00'),
                    'max_weight': Decimal('5.000'),
                    'cost': Decimal('2.40'),
                    'empty_weight': Decimal('0.200'),
                    'is_active': True,
                },
                {
                    'name': 'Medium Apparel & Cube Carton',
                    'code': 'BOX-MD-02',
                    'length': Decimal('35.00'),
                    'width': Decimal('32.00'),
                    'height': Decimal('22.00'),
                    'max_weight': Decimal('8.000'),
                    'cost': Decimal('3.50'),
                    'empty_weight': Decimal('0.350'),
                    'is_active': True,
                },
                {
                    'name': 'Large Standard Carton',
                    'code': 'BOX-LG-01',
                    'length': Decimal('48.00'),
                    'width': Decimal('38.00'),
                    'height': Decimal('30.00'),
                    'max_weight': Decimal('15.000'),
                    'cost': Decimal('5.20'),
                    'empty_weight': Decimal('0.550'),
                    'is_active': True,
                },
                {
                    'name': 'Extra Large Bulky Box',
                    'code': 'BOX-XL-01',
                    'length': Decimal('65.00'),
                    'width': Decimal('50.00'),
                    'height': Decimal('42.00'),
                    'max_weight': Decimal('25.000'),
                    'cost': Decimal('8.50'),
                    'empty_weight': Decimal('0.850'),
                    'is_active': True,
                },
                {
                    'name': 'Long Poster & Tube Box',
                    'code': 'BOX-LNG-01',
                    'length': Decimal('85.00'),
                    'width': Decimal('18.00'),
                    'height': Decimal('16.00'),
                    'max_weight': Decimal('6.000'),
                    'cost': Decimal('4.20'),
                    'empty_weight': Decimal('0.300'),
                    'is_active': True,
                },
                {
                    'name': 'Heavy Duty Industrial Freight Box',
                    'code': 'BOX-HD-01',
                    'length': Decimal('55.00'),
                    'width': Decimal('55.00'),
                    'height': Decimal('50.00'),
                    'max_weight': Decimal('45.000'),
                    'cost': Decimal('12.50'),
                    'empty_weight': Decimal('1.200'),
                    'is_active': True,
                },
            ]

            created_boxes = {}
            for b_data in boxes_data:
                box_obj, created = Box.objects.update_or_create(
                    code=b_data['code'],
                    defaults=b_data
                )
                created_boxes[box_obj.code] = box_obj
                status_str = "Created" if created else "Updated"
                self.stdout.write(f"  [{status_str}] Box: {box_obj.name} ({box_obj.code})")

            # 2. Seed Products
            products_data = [
                {
                    'name': 'Wireless Noise-Canceling Headphones',
                    'sku': 'ELEC-HP-01',
                    'length': Decimal('20.00'),
                    'width': Decimal('15.00'),
                    'height': Decimal('8.00'),
                    'weight': Decimal('0.450'),
                    'description': 'Premium over-ear Bluetooth headphones with case',
                },
                {
                    'name': 'Ergonomic Gaming Mouse',
                    'sku': 'ELEC-MS-01',
                    'length': Decimal('13.00'),
                    'width': Decimal('7.50'),
                    'height': Decimal('4.50'),
                    'weight': Decimal('0.120'),
                    'description': 'Lightweight optical RGB gaming mouse',
                },
                {
                    'name': 'Mechanical Keyboard',
                    'sku': 'ELEC-KB-02',
                    'length': Decimal('44.00'),
                    'width': Decimal('14.00'),
                    'height': Decimal('4.00'),
                    'weight': Decimal('1.150'),
                    'description': 'Tenkeyless RGB mechanical gaming keyboard',
                },
                {
                    'name': 'Ceramic Coffee Mug',
                    'sku': 'HOME-MUG-01',
                    'length': Decimal('12.00'),
                    'width': Decimal('10.00'),
                    'height': Decimal('11.00'),
                    'weight': Decimal('0.380'),
                    'description': '350ml artisanal ceramic coffee mug',
                },
                {
                    'name': 'Python Architecture Hardcover Book',
                    'sku': 'BOOK-PY-01',
                    'length': Decimal('24.00'),
                    'width': Decimal('18.00'),
                    'height': Decimal('3.50'),
                    'weight': Decimal('0.850'),
                    'description': 'Comprehensive textbook on software engineering and Python',
                },
                {
                    'name': 'Running Sneakers (Boxed)',
                    'sku': 'SHOE-RN-01',
                    'length': Decimal('32.00'),
                    'width': Decimal('20.00'),
                    'height': Decimal('12.00'),
                    'weight': Decimal('0.920'),
                    'description': 'Breathable athletic running shoes in retail box',
                },
                {
                    'name': 'Winter Down Puffer Jacket',
                    'sku': 'CLOTH-JK-01',
                    'length': Decimal('36.00'),
                    'width': Decimal('28.00'),
                    'height': Decimal('14.00'),
                    'weight': Decimal('1.350'),
                    'description': 'Insulated cold-weather travel jacket',
                },
                {
                    'name': 'Architectural Blueprint Poster (Rolled)',
                    'sku': 'ART-POST-01',
                    'length': Decimal('75.00'),
                    'width': Decimal('8.00'),
                    'height': Decimal('8.00'),
                    'weight': Decimal('0.320'),
                    'description': 'Rolled archival art print tube',
                },
                {
                    'name': 'Cast Iron Kettlebell 16kg',
                    'sku': 'GYM-KB-16',
                    'length': Decimal('22.00'),
                    'width': Decimal('20.00'),
                    'height': Decimal('26.00'),
                    'weight': Decimal('16.000'),
                    'description': 'Solid competition cast-iron kettlebell 16 kg',
                },
                {
                    'name': 'Insulated Stainless Steel Bottle (1L)',
                    'sku': 'HOME-BTL-01',
                    'length': Decimal('27.00'),
                    'width': Decimal('8.50'),
                    'height': Decimal('8.50'),
                    'weight': Decimal('0.480'),
                    'description': 'Double-walled vacuum insulated thermal bottle',
                },
            ]

            created_products = {}
            for p_data in products_data:
                prod_obj, created = Product.objects.update_or_create(
                    sku=p_data['sku'],
                    defaults=p_data
                )
                created_products[prod_obj.sku] = prod_obj
                status_str = "Created" if created else "Updated"
                self.stdout.write(f"  [{status_str}] Product: {prod_obj.name} ({prod_obj.sku})")

            # 3. Seed Sample Orders with realistic packing scenarios
            orders_scenario_data = [
                {
                    'order_number': 'ORD-2026-1001',
                    'customer_name': 'Sophia Martinez',
                    'items': [
                        ('ELEC-HP-01', 1),  # Headphones
                        ('ELEC-MS-01', 1),  # Mouse
                    ]
                },
                {
                    'order_number': 'ORD-2026-1002',
                    'customer_name': 'Liam Chen',
                    'items': [
                        ('BOOK-PY-01', 2),   # 2 Books
                        ('HOME-MUG-01', 1),  # 1 Coffee Mug
                    ]
                },
                {
                    'order_number': 'ORD-2026-1003',
                    'customer_name': 'Emma Watson',
                    'items': [
                        ('SHOE-RN-01', 1),   # Sneakers
                        ('CLOTH-JK-01', 1),  # Jacket
                    ]
                },
                {
                    'order_number': 'ORD-2026-1004',
                    'customer_name': 'Aarav Patel',
                    'items': [
                        ('ART-POST-01', 1),  # 75cm Rolled Poster
                        ('ELEC-MS-01', 1),   # Mouse
                    ]
                },
                {
                    'order_number': 'ORD-2026-1005',
                    'customer_name': 'Marcus Vance',
                    'items': [
                        ('GYM-KB-16', 1),    # 16kg Kettlebell (heavy!)
                        ('HOME-BTL-01', 1),  # Steel Bottle
                    ]
                },
            ]

            for o_data in orders_scenario_data:
                order_obj, created = Order.objects.update_or_create(
                    order_number=o_data['order_number'],
                    defaults={
                        'customer_name': o_data['customer_name'],
                        'status': 'PENDING',
                    }
                )
                # Clear existing items if any and recreate
                order_obj.items.all().delete()
                for sku, qty in o_data['items']:
                    product = created_products[sku]
                    OrderItem.objects.create(
                        order=order_obj,
                        product=product,
                        quantity=qty
                    )

                # Compute automatic recommendation
                result = RecommendationService.recommend_for_order(order_obj, persist=True)
                rec_name = result.recommended_box.name if result.recommended_box else "None"
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [Processed] Order #{order_obj.order_number} ({o_data['customer_name']}) -> "
                        f"Recommended: {rec_name} [Status: {result.status}]"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded all boxes, products, and test orders!"))
