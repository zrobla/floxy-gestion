from rest_framework import serializers

from content.models import ContentApproval, ContentItem, ContentMetric


class ContentApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentApproval
        fields = (
            "id",
            "content_item",
            "approved_by",
            "comment",
            "approved",
            "created_at",
        )
        read_only_fields = ("id", "approved_by", "created_at")


class ContentMetricSerializer(serializers.ModelSerializer):
    performance_score = serializers.FloatField(read_only=True)

    class Meta:
        model = ContentMetric
        fields = (
            "id",
            "content_item",
            "likes",
            "comments",
            "shares",
            "saves",
            "reach",
            "clicks",
            "performance_score",
            "created_at",
        )
        read_only_fields = ("id", "content_item", "performance_score", "created_at")


class ContentItemSerializer(serializers.ModelSerializer):
    approvals = ContentApprovalSerializer(many=True, read_only=True)
    metrics = ContentMetricSerializer(many=True, read_only=True)
    performance_score = serializers.SerializerMethodField()

    class Meta:
        model = ContentItem
        fields = (
            "id",
            "title",
            "description",
            "status",
            "platform",
            "scheduled_at",
            "created_by",
            "approved_by",
            "performance_score",
            "created_at",
            "updated_at",
            "approvals",
            "metrics",
        )
        read_only_fields = (
            "id",
            "created_by",
            "approved_by",
            "performance_score",
            "created_at",
            "updated_at",
        )

    def get_performance_score(self, obj):
        return obj.get_performance_score()

    def update(self, instance, validated_data):
        new_status = validated_data.pop("status", None)
        instance = super().update(instance, validated_data)
        if new_status:
            if new_status not in ContentItem.Status.values:
                raise serializers.ValidationError({"status": "Statut invalide."})
            instance.status = new_status
            instance.save(update_fields=["status", "updated_at"])
        return instance
