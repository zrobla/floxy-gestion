from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tasks.views import (
    RecurrenceRuleViewSet,
    TaskChecklistItemViewSet,
    TaskTemplateChecklistViewSet,
    TaskTemplateViewSet,
    TaskViewSet,
)

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")
router.register("checklists", TaskChecklistItemViewSet, basename="task-checklist")
router.register("recurrences", RecurrenceRuleViewSet, basename="recurrence")
router.register("templates", TaskTemplateViewSet, basename="task-template")
router.register(
    "template-checklists",
    TaskTemplateChecklistViewSet,
    basename="task-template-checklist",
)

urlpatterns = [
    path("", include(router.urls)),
]
