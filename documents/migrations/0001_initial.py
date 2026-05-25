# Generated manually for the initial document schema.
import django.db.models.deletion
from django.db import migrations, models

import documents.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("suppliers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SupplierDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="data de criacao")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="data de atualizacao")),
                ("document_type", models.CharField(choices=[("CONTRATO_SOCIAL", "Contrato social"), ("CARTAO_CNPJ", "Cartao CNPJ"), ("CERTIDAO_NEGATIVA", "Certidao negativa"), ("COMPROVANTE_BANCARIO", "Comprovante bancario"), ("COMPROVANTE_ENDERECO", "Comprovante de endereco"), ("ALVARA_LICENCA", "Alvara/licenca"), ("OUTRO", "Outro")], max_length=30, verbose_name="tipo de documento")),
                ("file", models.FileField(upload_to=documents.models.supplier_document_upload_path, verbose_name="arquivo")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True, verbose_name="data de envio")),
                ("expires_at", models.DateField(blank=True, null=True, verbose_name="data de validade")),
                ("status", models.CharField(choices=[("VALIDO", "Valido"), ("VENCIDO", "Vencido"), ("PENDENTE", "Pendente"), ("RECUSADO", "Recusado")], default="PENDENTE", max_length=10, verbose_name="situacao")),
                ("analysis_note", models.TextField(blank=True, verbose_name="observacao da analise")),
                ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="suppliers.supplier")),
            ],
            options={
                "verbose_name": "documento do fornecedor",
                "verbose_name_plural": "documentos dos fornecedores",
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.AddIndex(model_name="supplierdocument", index=models.Index(fields=["supplier", "document_type"], name="documents_s_supplier_1e5069_idx")),
        migrations.AddIndex(model_name="supplierdocument", index=models.Index(fields=["status"], name="documents_s_status_10ba50_idx")),
        migrations.AddIndex(model_name="supplierdocument", index=models.Index(fields=["expires_at"], name="documents_s_expires_ee8dd0_idx")),
    ]
