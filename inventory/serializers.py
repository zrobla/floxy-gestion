from django.core.exceptions import ValidationError
from rest_framework import serializers

from inventory.models import InventoryItem, StockMove


class InventoryItemSerializer(serializers.ModelSerializer):
    current_stock = serializers.SerializerMethodField()
    alert = serializers.SerializerMethodField()

    class Meta:
        model = InventoryItem
        fields = (
            "id",
            "name",
            "sku",
            "category",
            "min_stock",
            "current_stock",
            "alert",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "current_stock", "alert", "created_at", "updated_at")

    def get_current_stock(self, obj):
        return obj.get_current_stock()

    def get_alert(self, obj):
        stock_level = getattr(obj, "stock_level", None)
        if stock_level:
            return stock_level.alert
        return obj.get_current_stock() < obj.min_stock


class StockMoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMove
        fields = (
            "id",
            "item",
            "qty",
            "type",
            "reference",
            "created_at",
            "created_by",
        )
        read_only_fields = ("id", "created_at", "created_by")

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict or {"detail": str(exc)}
            ) from exc

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except ValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict or {"detail": str(exc)}
            ) from exc
