from rest_framework import serializers

from wigs.models import CareWig, WigProduct


class WigProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = WigProduct
        fields = (
            "id",
            "code",
            "name",
            "status",
            "price",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "code", "created_at", "updated_at")


class CareWigSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareWig
        fields = (
            "id",
            "code",
            "client",
            "status",
            "promised_date",
            "notes",
            "label_printed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "code",
            "label_printed_at",
            "created_at",
            "updated_at",
        )
