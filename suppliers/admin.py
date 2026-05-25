from django.contrib import admin
from django.utils import timezone

from documents.models import SupplierDocument
from suppliers.models import BankAccount, Supplier, SupplierCategory, SupplierContact


class SupplierContactInline(admin.TabularInline):
    model = SupplierContact
    extra = 0


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    extra = 0


class SupplierDocumentInline(admin.TabularInline):
    model = SupplierDocument
    extra = 0
    fields = ("document_type", "file", "uploaded_at", "expires_at", "status", "analysis_note")
    readonly_fields = ("uploaded_at",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("legal_name", "tax_id", "person_type", "category", "city", "status", "updated_at")
    list_filter = ("status", "category", "person_type", "state")
    search_fields = ("legal_name", "trade_name", "tax_id", "city", "category__name")
    readonly_fields = ("created_at", "updated_at")
    inlines = (SupplierContactInline, BankAccountInline, SupplierDocumentInline)
    actions = ("mark_as_active", "mark_as_inactive", "mark_as_blocked")
    fieldsets = (
        ("Identificacao", {"fields": ("person_type", "legal_name", "trade_name", "tax_id", "status")}),
        ("Registros", {"fields": ("state_registration", "municipal_registration")}),
        ("Contato", {"fields": ("email", "phone", "whatsapp")}),
        ("Endereco", {"fields": ("zip_code", "street", "number", "complement", "district", "city", "state", "country")}),
        ("Classificacao", {"fields": ("category", "products_services", "internal_notes")}),
        ("Auditoria", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")

    @admin.action(description="Marcar fornecedores selecionados como ativos")
    def mark_as_active(self, request, queryset):
        queryset.update(status=Supplier.Status.ACTIVE, updated_at=timezone.now())

    @admin.action(description="Marcar fornecedores selecionados como inativos")
    def mark_as_inactive(self, request, queryset):
        queryset.update(status=Supplier.Status.INACTIVE, updated_at=timezone.now())

    @admin.action(description="Marcar fornecedores selecionados como bloqueados")
    def mark_as_blocked(self, request, queryset):
        queryset.update(status=Supplier.Status.BLOCKED, updated_at=timezone.now())


@admin.register(SupplierCategory)
class SupplierCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(SupplierContact)
class SupplierContactAdmin(admin.ModelAdmin):
    list_display = ("name", "supplier", "role", "email", "phone")
    search_fields = ("name", "supplier__legal_name", "email")
    list_filter = ("supplier__category",)
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("supplier", "supplier__category")


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("supplier", "bank", "branch", "account", "account_type", "validation_status")
    list_filter = ("validation_status", "account_type", "bank")
    search_fields = ("supplier__legal_name", "holder_name", "holder_tax_id", "bank")
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("supplier")
