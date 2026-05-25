from django.db import models

from core.models import TimeStampedModel


class IntegrationLog(TimeStampedModel):
    source_system = models.CharField("sistema origem", max_length=120)
    target_system = models.CharField("sistema destino", max_length=120)
    endpoint = models.URLField("endpoint", max_length=500)
    http_method = models.CharField("metodo HTTP", max_length=10)
    request_status = models.PositiveSmallIntegerField("status da requisicao", null=True, blank=True)
    request_payload = models.JSONField("payload enviado", null=True, blank=True)
    response_payload = models.JSONField("resposta recebida", null=True, blank=True)
    error = models.TextField("erro", blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "log de integracao"
        verbose_name_plural = "logs de integracao"

    def __str__(self):
        return f"{self.source_system} -> {self.target_system} ({self.http_method})"
