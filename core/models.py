from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("data de criacao", auto_now_add=True)
    updated_at = models.DateTimeField("data de atualizacao", auto_now=True)

    class Meta:
        abstract = True
