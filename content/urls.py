from django.urls import include, path
from rest_framework.routers import DefaultRouter

from content.views import ContentItemViewSet

router = DefaultRouter()
router.register("items", ContentItemViewSet, basename="content-item")

urlpatterns = [
    path("", include(router.urls)),
]
