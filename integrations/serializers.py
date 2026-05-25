from rest_framework import serializers

from integrations.models import IntegrationLog


class IntegrationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationLog
        fields = [
            "id",
            "source_system",
            "target_system",
            "endpoint",
            "http_method",
            "request_status",
            "request_payload",
            "response_payload",
            "error",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
