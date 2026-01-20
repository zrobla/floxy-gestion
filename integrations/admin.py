from django.contrib import admin

from integrations.models import LoyverseReceipt, LoyverseStore


@admin.register(LoyverseStore)
class LoyverseStoreAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    search_fields = ("token",)
    ordering = ("-created_at",)


@admin.register(LoyverseReceipt)
class LoyverseReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_id", "created_at")
    search_fields = ("receipt_id",)
    ordering = ("-created_at",)
