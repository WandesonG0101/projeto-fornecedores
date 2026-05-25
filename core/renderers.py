from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """Wraps API responses in a predictable envelope for integrations."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None

        if response and response.exception:
            payload = {"success": False, "error": data}
        elif isinstance(data, dict) and {"count", "results"}.issubset(data.keys()):
            payload = {
                "success": True,
                "data": data.get("results"),
                "meta": {
                    "count": data.get("count"),
                    "next": data.get("next"),
                    "previous": data.get("previous"),
                },
            }
        else:
            payload = {"success": True, "data": data}

        return super().render(payload, accepted_media_type, renderer_context)
