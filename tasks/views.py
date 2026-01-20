from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from tasks.models import (
    RecurrenceRule,
    Task,
    TaskChecklistItem,
    TaskTemplate,
    TaskTemplateChecklist,
)
from tasks.permissions import ManagerAdminPermission, TaskPermission
from tasks.serializers import (
    RecurrenceRuleSerializer,
    TaskChecklistItemSerializer,
    TaskSerializer,
    TaskTemplateChecklistSerializer,
    TaskTemplateSerializer,
)


class RecurrenceRuleViewSet(viewsets.ModelViewSet):
    queryset = RecurrenceRule.objects.all()
    serializer_class = RecurrenceRuleSerializer
    permission_classes = [ManagerAdminPermission]


class TaskTemplateViewSet(viewsets.ModelViewSet):
    queryset = TaskTemplate.objects.all()
    serializer_class = TaskTemplateSerializer
    permission_classes = [ManagerAdminPermission]


class TaskTemplateChecklistViewSet(viewsets.ModelViewSet):
    queryset = TaskTemplateChecklist.objects.select_related("template")
    serializer_class = TaskTemplateChecklistSerializer
    permission_classes = [ManagerAdminPermission]


class TaskChecklistItemViewSet(viewsets.ModelViewSet):
    queryset = TaskChecklistItem.objects.select_related("task")
    serializer_class = TaskChecklistItemSerializer
    permission_classes = [TaskPermission]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related("assigned_to", "created_by", "template")
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return queryset.none()
        if user.role == "STAFF":
            return queryset.filter(assigned_to=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            raise DRFValidationError({"status": "Le statut est obligatoire."})
        try:
            task.set_status(new_status)
        except ValidationError as exc:
            raise DRFValidationError({"status": str(exc)}) from exc
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
