import requests

from integrations.models import IntegrationLog


class IntegrationAPIClient:
    """Small client layer to keep external API communication outside views."""

    def __init__(self, source_system, target_system, timeout=20):
        self.source_system = source_system
        self.target_system = target_system
        self.timeout = timeout

    def request(self, method, endpoint, payload=None, headers=None):
        log = IntegrationLog.objects.create(
            source_system=self.source_system,
            target_system=self.target_system,
            endpoint=endpoint,
            http_method=method.upper(),
            request_payload=payload,
        )
        try:
            response = requests.request(method, endpoint, json=payload, headers=headers, timeout=self.timeout)
            try:
                response_payload = response.json()
            except ValueError:
                response_payload = {"raw": response.text}

            log.request_status = response.status_code
            log.response_payload = response_payload
            log.save(update_fields=["request_status", "response_payload", "updated_at"])
            response.raise_for_status()
            return response_payload
        except requests.RequestException as exc:
            log.error = str(exc)
            log.save(update_fields=["error", "updated_at"])
            raise
