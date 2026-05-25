from pathlib import Path

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from core.permissions import can_analyze_supplier_data
from documents.models import SupplierDocument


ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


class SupplierDocumentSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.legal_name", read_only=True)

    class Meta:
        model = SupplierDocument
        fields = [
            "id",
            "supplier",
            "supplier_name",
            "document_type",
            "file",
            "uploaded_at",
            "expires_at",
            "status",
            "analysis_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "supplier_name", "uploaded_at", "created_at", "updated_at"]

    def validate_file(self, value):
        extension = Path(value.name).suffix.lower()
        if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise serializers.ValidationError("Formato de arquivo nao permitido. Use PDF, PNG ou JPG.")

        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(f"Arquivo excede o limite de {settings.MAX_UPLOAD_SIZE_MB} MB.")

        return value

    def validate(self, attrs):
        request = self.context.get("request")
        new_status = attrs.get("status")
        current_status = getattr(self.instance, "status", None)
        status_changed = new_status and new_status != current_status
        analysis_statuses = {
            SupplierDocument.Status.VALID,
            SupplierDocument.Status.REJECTED,
            SupplierDocument.Status.EXPIRED,
        }
        if status_changed and new_status in analysis_statuses:
            if not request or not can_analyze_supplier_data(request.user):
                raise serializers.ValidationError({"status": "Somente analistas ou administradores podem concluir analise documental."})

        expires_at = attrs.get("expires_at") or getattr(self.instance, "expires_at", None)
        status = attrs.get("status") or getattr(self.instance, "status", None)
        if expires_at and status == SupplierDocument.Status.VALID:
            if expires_at < timezone.localdate():
                raise serializers.ValidationError({"status": "Documento vencido nao pode ser marcado como valido."})
        return attrs
