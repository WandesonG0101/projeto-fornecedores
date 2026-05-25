from django.contrib import admin

from documents.models import SupplierDocument


@admin.register(SupplierDocument)
class SupplierDocumentAdmin(admin.ModelAdmin):
    list_display = ("supplier", "document_type", "status", "uploaded_at", "expires_at")
    list_filter = ("document_type", "status", "expires_at")
    search_fields = ("supplier__legal_name", "supplier__tax_id", "analysis_note")
    readonly_fields = ("created_at", "updated_at", "uploaded_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("supplier")
