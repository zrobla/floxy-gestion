from django.contrib import admin

from content.models import ContentApproval, ContentItem, ContentMetric


class ContentApprovalInline(admin.TabularInline):
    model = ContentApproval
    extra = 0
    readonly_fields = ("created_at",)


class ContentMetricInline(admin.TabularInline):
    model = ContentMetric
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "platform",
        "scheduled_at",
        "created_by",
        "approved_by",
    )
    list_filter = ("status", "platform")
    search_fields = ("title", "description")
    ordering = ("-created_at",)
    inlines = [ContentApprovalInline, ContentMetricInline]


@admin.register(ContentApproval)
class ContentApprovalAdmin(admin.ModelAdmin):
    list_display = ("content_item", "approved", "approved_by", "created_at")
    list_filter = ("approved",)
    search_fields = ("content_item__title", "comment")
    ordering = ("-created_at",)


@admin.register(ContentMetric)
class ContentMetricAdmin(admin.ModelAdmin):
    list_display = ("content_item", "likes", "comments", "reach", "created_at")
    search_fields = ("content_item__title",)
    ordering = ("-created_at",)
