from django.urls import include, path
from rest_framework.routers import DefaultRouter

from operations.views import ActivityLineViewSet, ActivityViewSet, ServiceViewSet

router = DefaultRouter()
router.register("services", ServiceViewSet, basename="service")
router.register("activities", ActivityViewSet, basename="activity")
router.register("activity-lines", ActivityLineViewSet, basename="activity-line")

urlpatterns = [
    path("", include(router.urls)),
]
