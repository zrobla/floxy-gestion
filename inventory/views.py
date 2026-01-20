from rest_framework import viewsets

from inventory.models import InventoryItem, StockMove
from inventory.serializers import InventoryItemSerializer, StockMoveSerializer


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer


class StockMoveViewSet(viewsets.ModelViewSet):
    queryset = StockMove.objects.select_related("item", "created_by")
    serializer_class = StockMoveSerializer

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user)
