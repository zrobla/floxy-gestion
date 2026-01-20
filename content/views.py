from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from content.models import ContentApproval, ContentItem
from content.permissions import ContentItemPermission, OwnerOnlyPermission
from content.serializers import ContentItemSerializer, ContentMetricSerializer


class ContentItemViewSet(viewsets.ModelViewSet):
    queryset = ContentItem.objects.prefetch_related("approvals", "metrics")
    serializer_class = ContentItemSerializer
    permission_classes = [ContentItemPermission]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def submit_for_approval(self, request, pk=None):
        content_item = self.get_object()
        try:
            content_item.submit_for_approval()
        except ValidationError as exc:
            raise DRFValidationError({"detail": str(exc)}) from exc
        return Response(
            self.get_serializer(content_item).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[OwnerOnlyPermission])
    def approve(self, request, pk=None):
        content_item = self.get_object()
        comment = request.data.get("comment", "").strip()
        try:
            content_item.approve(request.user, comment)
        except ValidationError as exc:
            raise DRFValidationError({"comment": str(exc)}) from exc
        ContentApproval.objects.create(
            content_item=content_item,
            approved_by=request.user,
            comment=comment,
            approved=True,
        )
        return Response(
            self.get_serializer(content_item).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[OwnerOnlyPermission])
    def reject(self, request, pk=None):
        content_item = self.get_object()
        comment = request.data.get("comment", "").strip()
        try:
            content_item.reject(request.user, comment)
        except ValidationError as exc:
            raise DRFValidationError({"comment": str(exc)}) from exc
        ContentApproval.objects.create(
            content_item=content_item,
            approved_by=request.user,
            comment=comment,
            approved=False,
        )
        return Response(
            self.get_serializer(content_item).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        content_item = self.get_object()
        try:
            content_item.publish()
        except ValidationError as exc:
            raise DRFValidationError({"detail": str(exc)}) from exc
        return Response(
            self.get_serializer(content_item).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def add_metrics(self, request, pk=None):
        content_item = self.get_object()
        serializer = ContentMetricSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        metric = serializer.save(content_item=content_item)
        try:
            content_item.record_metrics()
        except ValidationError as exc:
            raise DRFValidationError({"detail": str(exc)}) from exc
        response_data = ContentMetricSerializer(metric).data
        return Response(response_data, status=status.HTTP_201_CREATED)
