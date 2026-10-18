import unittest
from boxes.services.packer import (
    PackingService,
    ItemToPack,
    BoxCandidate,
    PlacedItem,
)


class PackingServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.small_box = BoxCandidate(
            id=1,
            name="Small Box",
            code="BOX-SM",
            length=20.0,
            width=15.0,
            height=10.0,
            max_weight=2.0,
            cost=1.50,
            empty_weight=0.1
        )
        self.medium_box = BoxCandidate(
            id=2,
            name="Medium Box",
            code="BOX-MD",
            length=30.0,
            width=25.0,
            height=20.0,
            max_weight=6.0,
            cost=3.00,
            empty_weight=0.2
        )
        self.large_box = BoxCandidate(
            id=3,
            name="Large Box",
            code="BOX-LG",
            length=50.0,
            width=40.0,
            height=30.0,
            max_weight=15.0,
            cost=5.50,
            empty_weight=0.5
        )

    def test_rotations_generation(self):
        # Distinct dimensions: 6 rotations
        rots = PackingService.get_rotations(10.0, 20.0, 30.0)
        self.assertEqual(len(rots), 6)
        self.assertIn((10.0, 20.0, 30.0), rots)
        self.assertIn((30.0, 20.0, 10.0), rots)

        # Cube: only 1 unique rotation
        rots_cube = PackingService.get_rotations(10.0, 10.0, 10.0)
        self.assertEqual(len(rots_cube), 1)

        # Two equal dimensions: 3 unique rotations
        rots_square_face = PackingService.get_rotations(10.0, 10.0, 20.0)
        self.assertEqual(len(rots_square_face), 3)

    def test_3d_overlap_detection(self):
        p1 = PlacedItem(
            item_id="1",
            name="Item 1",
            sku="S1",
            x=0.0, y=0.0, z=0.0,
            dx=10.0, dy=10.0, dz=10.0,
            weight=1.0
        )
        # Inside p1: overlaps
        self.assertTrue(PackingService._is_overlap(p1, 2.0, 2.0, 2.0, 5.0, 5.0, 5.0))

        # Touching adjacent face along X: does NOT overlap
        self.assertFalse(PackingService._is_overlap(p1, 10.0, 0.0, 0.0, 5.0, 5.0, 5.0))

        # Completely outside: does NOT overlap
        self.assertFalse(PackingService._is_overlap(p1, 15.0, 15.0, 15.0, 5.0, 5.0, 5.0))

    def test_single_item_rotation_fit(self):
        # Item dimensions 9.0 x 18.0 x 14.0 fits in small box (20 x 15 x 10)
        # when rotated as (18.0, 14.0, 9.0)
        item = ItemToPack(
            id=101,
            name="Rotated Item",
            length=9.0,
            width=18.0,
            height=14.0,
            weight=1.2,
            quantity=1
        )
        eval_res = PackingService.evaluate_box(self.small_box, [item])
        self.assertTrue(eval_res.fits, f"Item should fit with rotation: {eval_res.rejection_reason}")

    def test_weight_capacity_rejection(self):
        # Item weight 3.0 kg > small box max weight (2.0 kg)
        item = ItemToPack(
            id=102,
            name="Heavy Item",
            length=10.0,
            width=10.0,
            height=5.0,
            weight=3.0,
            quantity=1
        )
        eval_res = PackingService.evaluate_box(self.small_box, [item])
        self.assertFalse(eval_res.fits)
        self.assertIn("exceeds box capacity", eval_res.rejection_reason)

    def test_volume_capacity_rejection(self):
        # 10 items of 15x10x8 = 12000 cm3 > small box volume (3000 cm3)
        item = ItemToPack(
            id=103,
            name="Voluminous Item",
            length=15.0,
            width=10.0,
            height=8.0,
            weight=0.1,
            quantity=10
        )
        eval_res = PackingService.evaluate_box(self.small_box, [item])
        self.assertFalse(eval_res.fits)
        self.assertIn("exceeds box volume", eval_res.rejection_reason)

    def test_dimensional_boundary_rejection(self):
        # Item has a dimension of 25cm, but small box max dimension is 20cm
        item = ItemToPack(
            id=104,
            name="Too Long Item",
            length=25.0,
            width=5.0,
            height=5.0,
            weight=0.5,
            quantity=1
        )
        eval_res = PackingService.evaluate_box(self.small_box, [item])
        self.assertFalse(eval_res.fits)
        self.assertIn("exceeds box boundaries", eval_res.rejection_reason)

    def test_cost_minimization_recommendation(self):
        # Both Small Box ($1.50) and Medium Box ($3.00) can fit this item
        # System must pick the cheapest eligible box (Small Box)
        item = ItemToPack(
            id=105,
            name="Small Gadget",
            length=12.0,
            width=10.0,
            height=5.0,
            weight=0.4,
            quantity=1
        )
        res = PackingService.recommend_box([item], [self.large_box, self.small_box, self.medium_box])
        self.assertTrue(res.success)
        self.assertEqual(res.recommended_box.id, self.small_box.id)
        self.assertEqual(res.recommended_box.cost, 1.50)
        self.assertGreater(len(res.alternative_boxes), 0)

    def test_tie_breaking_by_smaller_volume(self):
        # Create two boxes with the EXACT same cost, but different sizes
        box_compact = BoxCandidate(
            id=10, name="Compact Box", code="C-1",
            length=20.0, width=20.0, height=10.0, max_weight=5.0, cost=2.00
        )
        box_loose = BoxCandidate(
            id=11, name="Loose Box", code="L-1",
            length=30.0, width=30.0, height=20.0, max_weight=5.0, cost=2.00
        )
        item = ItemToPack(
            id=106, name="Small Book",
            length=15.0, width=15.0, height=5.0, weight=0.5, quantity=1
        )
        res = PackingService.recommend_box([item], [box_loose, box_compact])
        self.assertTrue(res.success)
        # Should pick the more compact box to minimize empty void volume
        self.assertEqual(res.recommended_box.id, box_compact.id)

    def test_multi_box_plan_generation(self):
        # Create items that exceed any single box
        # Large box max weight is 15kg. Let's create two 10kg items (total 20kg).
        item = ItemToPack(
            id=107,
            name="Heavy Part",
            length=20.0,
            width=20.0,
            height=15.0,
            weight=10.0,
            quantity=2
        )
        # Neither small (2kg), medium (6kg), nor large (15kg) can hold both items together (20kg)
        res = PackingService.recommend_box([item], [self.small_box, self.medium_box, self.large_box])
        self.assertTrue(res.success)
        self.assertEqual(res.status, 'MULTI_BOX_NEEDED')
        self.assertEqual(len(res.multi_box_packages), 2)
        # Each item should be in its own box
        self.assertEqual(res.multi_box_packages[0].box.id, self.large_box.id)
        self.assertEqual(res.multi_box_packages[1].box.id, self.large_box.id)

    def test_empty_items_returns_no_fit(self):
        res = PackingService.recommend_box([], [self.small_box])
        self.assertFalse(res.success)
        self.assertEqual(res.status, 'NO_FIT')
