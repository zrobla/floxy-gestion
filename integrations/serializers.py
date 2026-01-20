from rest_framework import serializers

from integrations.models import LoyverseReceipt, LoyverseStore


class LoyverseStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyverseStore
        fields = ("id", "token", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class LoyverseReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyverseReceipt
        fields = ("id", "receipt_id", "raw_json", "created_at")
        read_only_fields = ("id", "receipt_id", "created_at")
