from django.urls import include, path
from rest_framework.routers import DefaultRouter

from inventory.views import InventoryItemViewSet, StockMoveViewSet

router = DefaultRouter()
router.register("items", InventoryItemViewSet, basename="inventory-item")
router.register("moves", StockMoveViewSet, basename="stock-move")

urlpatterns = [
    path("", include(router.urls)),
]
