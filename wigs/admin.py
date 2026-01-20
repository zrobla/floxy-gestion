from django.contrib import admin

from wigs.models import CareWig, Sequence, WigProduct


@admin.register(Sequence)
class SequenceAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "updated_at")
    search_fields = ("key",)
    ordering = ("key",)


@admin.register(WigProduct)
class WigProductAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "status", "price", "created_at")
    list_filter = ("status",)
    search_fields = ("code", "name")
    ordering = ("-created_at",)


@admin.register(CareWig)
class CareWigAdmin(admin.ModelAdmin):
    list_display = ("code", "client", "status", "promised_date", "label_printed_at")
    list_filter = ("status",)
    search_fields = ("code", "client")
    ordering = ("-created_at",)
