from rest_framework import mixins, viewsets

from core.permissions import AdminRolePermission
from integrations.models import IntegrationLog
from integrations.serializers import IntegrationLogSerializer


class IntegrationLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = IntegrationLog.objects.all()
    serializer_class = IntegrationLogSerializer
    permission_classes = [AdminRolePermission]
    filterset_fields = ["source_system", "target_system", "http_method", "request_status"]
    search_fields = ["endpoint", "error", "source_system", "target_system"]
    ordering_fields = ["created_at", "request_status"]
