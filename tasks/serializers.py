from django.core.exceptions import ValidationError
from rest_framework import serializers

from tasks.models import (
    RecurrenceRule,
    Task,
    TaskChecklistItem,
    TaskTemplate,
    TaskTemplateChecklist,
)


class RecurrenceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurrenceRule
        fields = (
            "id",
            "name",
            "frequency",
            "interval",
            "weekdays",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TaskTemplateChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplateChecklist
        fields = ("id", "template", "label", "order", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class TaskTemplateSerializer(serializers.ModelSerializer):
    checklist_items = TaskTemplateChecklistSerializer(many=True, read_only=True)

    class Meta:
        model = TaskTemplate
        fields = (
            "id",
            "name",
            "description",
            "recurrence_rule",
            "is_active",
            "created_at",
            "updated_at",
            "checklist_items",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TaskChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskChecklistItem
        fields = ("id", "task", "label", "is_done", "order", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class TaskSerializer(serializers.ModelSerializer):
    checklist_items = TaskChecklistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "assigned_to",
            "created_by",
            "due_date",
            "template",
            "created_at",
            "updated_at",
            "checklist_items",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def update(self, instance, validated_data):
        new_status = validated_data.pop("status", None)
        instance = super().update(instance, validated_data)
        if new_status:
            try:
                instance.set_status(new_status)
            except ValidationError as exc:
                raise serializers.ValidationError({"status": str(exc)}) from exc
        return instance
