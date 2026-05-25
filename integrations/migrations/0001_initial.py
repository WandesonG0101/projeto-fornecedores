# Generated manually for the initial integration log schema.
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="IntegrationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="data de criacao")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="data de atualizacao")),
                ("source_system", models.CharField(max_length=120, verbose_name="sistema origem")),
                ("target_system", models.CharField(max_length=120, verbose_name="sistema destino")),
                ("endpoint", models.URLField(max_length=500, verbose_name="endpoint")),
                ("http_method", models.CharField(max_length=10, verbose_name="metodo HTTP")),
                ("request_status", models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="status da requisicao")),
                ("request_payload", models.JSONField(blank=True, null=True, verbose_name="payload enviado")),
                ("response_payload", models.JSONField(blank=True, null=True, verbose_name="resposta recebida")),
                ("error", models.TextField(blank=True, verbose_name="erro")),
            ],
            options={
                "verbose_name": "log de integracao",
                "verbose_name_plural": "logs de integracao",
                "ordering": ["-created_at"],
            },
        ),
    ]
