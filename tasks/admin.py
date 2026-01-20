from django.contrib import admin

from tasks.models import (
    RecurrenceRule,
    Task,
    TaskChecklistItem,
    TaskTemplate,
    TaskTemplateChecklist,
)


@admin.register(RecurrenceRule)
class RecurrenceRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "frequency", "interval", "weekdays", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


class TaskChecklistInline(admin.TabularInline):
    model = TaskChecklistItem
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "assigned_to", "due_date", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "description")
    ordering = ("-created_at",)
    inlines = [TaskChecklistInline]


class TaskTemplateChecklistInline(admin.TabularInline):
    model = TaskTemplateChecklist
    extra = 0


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "recurrence_rule", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)
    inlines = [TaskTemplateChecklistInline]


@admin.register(TaskChecklistItem)
class TaskChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("task", "label", "is_done", "order")
    list_filter = ("is_done",)
    search_fields = ("label",)
    ordering = ("task", "order")


@admin.register(TaskTemplateChecklist)
class TaskTemplateChecklistAdmin(admin.ModelAdmin):
    list_display = ("template", "label", "order")
    search_fields = ("label",)
    ordering = ("template", "order")
