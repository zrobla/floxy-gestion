from django.utils import timezone
from rest_framework import serializers

from operations.models import Activity, ActivityLine, Service


class PaymentLinkSerializer(serializers.Serializer):
    receipt_id = serializers.IntegerField(required=False)
    manual_reference = serializers.CharField(required=False, allow_blank=True)
    final_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "description",
            "category",
            "category_name",
            "base_price",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ActivityLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLine
        fields = (
            "id",
            "activity",
            "service",
            "description",
            "quantity",
            "unit_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ActivitySerializer(serializers.ModelSerializer):
    lines = ActivityLineSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = (
            "id",
            "type",
            "status",
            "client",
            "assigned_staff",
            "start_at",
            "estimated_end_at",
            "end_at",
            "expected_amount",
            "final_amount",
            "notes",
            "content_possible",
            "created_at",
            "updated_at",
            "lines",
        )
        read_only_fields = (
            "id",
            "start_at",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        start_at = self.instance.start_at if self.instance else timezone.now()
        estimated_end_at = attrs.get("estimated_end_at")
        end_at = attrs.get("end_at")

        if estimated_end_at and estimated_end_at < start_at:
            raise serializers.ValidationError(
                {"estimated_end_at": "La fin estimée doit être après le début."}
            )
        if end_at and end_at < start_at:
            raise serializers.ValidationError(
                {"end_at": "La fin réelle doit être après le début."}
            )
        return attrs

    def update(self, instance, validated_data):
        new_status = validated_data.pop("status", None)
        instance = super().update(instance, validated_data)
        if new_status:
            instance.set_status(new_status)
        return instance
