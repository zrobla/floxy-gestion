from django.core.exceptions import ValidationError
from django.test import TestCase

from inventory.models import InventoryItem, StockLevel, StockMove


class StockComputationTests(TestCase):
    def test_stock_updates_after_moves(self):
        item = InventoryItem.objects.create(
            name="Shampoing", category=InventoryItem.Category.CONSUMABLE, min_stock=6
        )

        StockMove.objects.create(item=item, qty=10, type=StockMove.Type.IN)
        StockMove.objects.create(item=item, qty=4, type=StockMove.Type.OUT)
        StockMove.objects.create(item=item, qty=-1, type=StockMove.Type.ADJUST)

        self.assertEqual(item.get_current_stock(), 5)

        stock_level = StockLevel.objects.get(item=item)
        self.assertEqual(stock_level.quantity, 5)
        self.assertTrue(stock_level.alert)


class StockValidationTests(TestCase):
    def test_prevent_negative_stock(self):
        item = InventoryItem.objects.create(
            name="Brosse", category=InventoryItem.Category.SALE
        )

        with self.assertRaises(ValidationError):
            StockMove.objects.create(item=item, qty=1, type=StockMove.Type.OUT)
