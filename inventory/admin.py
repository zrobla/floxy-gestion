from django.contrib import admin

from inventory.models import InventoryItem, StockLevel, StockMove


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "min_stock", "current_stock")
    list_filter = ("category",)
    search_fields = ("name", "sku")
    ordering = ("name",)

    @admin.display(description="Stock actuel")
    def current_stock(self, obj):
        return obj.get_current_stock()


@admin.register(StockMove)
class StockMoveAdmin(admin.ModelAdmin):
    list_display = ("item", "type", "qty", "reference", "created_at", "created_by")
    list_filter = ("type",)
    search_fields = ("item__name", "reference")
    ordering = ("-created_at",)


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = ("item", "quantity", "alert", "updated_at")
    list_filter = ("alert",)
    search_fields = ("item__name",)
