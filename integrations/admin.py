from django.contrib import admin

from integrations.models import IntegrationLog


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ("source_system", "target_system", "http_method", "request_status", "created_at")
    list_filter = ("source_system", "target_system", "http_method", "request_status")
    search_fields = ("endpoint", "error", "source_system", "target_system")
    readonly_fields = ("created_at", "updated_at")
