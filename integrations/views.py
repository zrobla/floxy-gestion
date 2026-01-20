from rest_framework import viewsets

from integrations.models import LoyverseStore
from integrations.permissions import AdminOnlyPermission
from integrations.serializers import LoyverseStoreSerializer


class LoyverseStoreViewSet(viewsets.ModelViewSet):
    queryset = LoyverseStore.objects.all()
    serializer_class = LoyverseStoreSerializer
    permission_classes = [AdminOnlyPermission]
