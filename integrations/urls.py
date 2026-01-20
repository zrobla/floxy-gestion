from django.urls import include, path
from rest_framework.routers import DefaultRouter

from integrations.views import LoyverseStoreViewSet

router = DefaultRouter()
router.register("loyverse-stores", LoyverseStoreViewSet, basename="loyverse-store")

urlpatterns = [
    path("", include(router.urls)),
]
