from rest_framework import viewsets

from core.permissions import SupplierAPIPermission
from documents.models import SupplierDocument
from documents.serializers import SupplierDocumentSerializer


class SupplierDocumentViewSet(viewsets.ModelViewSet):
    queryset = SupplierDocument.objects.select_related("supplier").all()
    serializer_class = SupplierDocumentSerializer
    permission_classes = [SupplierAPIPermission]
    filterset_fields = ["supplier", "document_type", "status", "expires_at"]
    search_fields = ["supplier__legal_name", "supplier__tax_id", "analysis_note"]
    ordering_fields = ["uploaded_at", "expires_at", "status"]
