from django.contrib import admin

from operations.models import Activity, ActivityLine, PaymentLink, Service, ServiceCategory


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "base_price", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("name", "description")
    ordering = ("name",)


class ActivityLineInline(admin.TabularInline):
    model = ActivityLine
    extra = 0


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "status",
        "client",
        "assigned_staff",
        "start_at",
        "expected_amount",
    )
    list_filter = ("status", "type", "content_possible")
    search_fields = ("client", "notes")
    ordering = ("-start_at",)
    inlines = [ActivityLineInline]


@admin.register(ActivityLine)
class ActivityLineAdmin(admin.ModelAdmin):
    list_display = ("id", "activity", "service", "quantity", "unit_price")
    list_filter = ("service",)
    search_fields = ("description",)


@admin.register(PaymentLink)
class PaymentLinkAdmin(admin.ModelAdmin):
    list_display = ("activity", "manual_reference", "loyverse_receipt", "created_at")
    search_fields = ("activity__client", "manual_reference")
    ordering = ("-created_at",)
