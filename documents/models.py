from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel


def supplier_document_upload_path(instance, filename):
    return f"suppliers/{instance.supplier_id}/documents/{filename}"


class SupplierDocument(TimeStampedModel):
    class DocumentType(models.TextChoices):
        SOCIAL_CONTRACT = "CONTRATO_SOCIAL", "Contrato social"
        CNPJ_CARD = "CARTAO_CNPJ", "Cartao CNPJ"
        NEGATIVE_CERTIFICATE = "CERTIDAO_NEGATIVA", "Certidao negativa"
        BANK_PROOF = "COMPROVANTE_BANCARIO", "Comprovante bancario"
        ADDRESS_PROOF = "COMPROVANTE_ENDERECO", "Comprovante de endereco"
        LICENSE = "ALVARA_LICENCA", "Alvara/licenca"
        OTHER = "OUTRO", "Outro"

    class Status(models.TextChoices):
        VALID = "VALIDO", "Valido"
        EXPIRED = "VENCIDO", "Vencido"
        PENDING = "PENDENTE", "Pendente"
        REJECTED = "RECUSADO", "Recusado"

    supplier = models.ForeignKey("suppliers.Supplier", related_name="documents", on_delete=models.CASCADE)
    document_type = models.CharField("tipo de documento", max_length=30, choices=DocumentType.choices)
    file = models.FileField("arquivo", upload_to=supplier_document_upload_path)
    uploaded_at = models.DateTimeField("data de envio", auto_now_add=True)
    expires_at = models.DateField("data de validade", null=True, blank=True)
    status = models.CharField("situacao", max_length=10, choices=Status.choices, default=Status.PENDING)
    analysis_note = models.TextField("observacao da analise", blank=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "documento do fornecedor"
        verbose_name_plural = "documentos dos fornecedores"
        indexes = [
            models.Index(fields=["supplier", "document_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.supplier} - {self.get_document_type_display()}"

    def clean(self):
        super().clean()
        if self.expires_at and self.expires_at < timezone.localdate() and self.status == self.Status.VALID:
            raise ValidationError({"status": "Documento vencido nao pode permanecer valido."})
