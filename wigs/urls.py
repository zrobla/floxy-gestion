from django.urls import include, path
from rest_framework.routers import DefaultRouter

from wigs.views import CareWigViewSet, WigProductViewSet, care_wig_label

router = DefaultRouter()
router.register("products", WigProductViewSet, basename="wig-product")
router.register("care", CareWigViewSet, basename="care-wig")

urlpatterns = [
    path("care-wigs/<int:pk>/label.pdf", care_wig_label, name="care-wig-label"),
    path("", include(router.urls)),
]
