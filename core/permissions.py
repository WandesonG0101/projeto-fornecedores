from rest_framework.permissions import SAFE_METHODS, BasePermission


ROLE_ADMIN = "Administrador"
ROLE_CADASTRADOR = "Cadastrador"
ROLE_ANALISTA = "Analista"
ROLE_LEITURA = "Somente leitura"


def user_in_groups(user, groups):
    return bool(user and user.is_authenticated and user.groups.filter(name__in=groups).exists())


def can_view_sensitive_supplier_data(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user_in_groups(user, [ROLE_ADMIN]):
        return True
    return user_in_groups(user, [ROLE_CADASTRADOR, ROLE_ANALISTA])


def can_analyze_supplier_data(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user_in_groups(user, [ROLE_ADMIN]):
        return True
    return user_in_groups(user, [ROLE_ANALISTA])


class SupplierAPIPermission(BasePermission):
    """
    Initial role policy:
    - admin: full access
    - cadastrador: create and edit suppliers/documents
    - analista: analyze documents and edit validation status
    - somente leitura: read-only access
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user_in_groups(user, [ROLE_ADMIN]):
            return True
        if request.method in SAFE_METHODS:
            return user_in_groups(user, [ROLE_CADASTRADOR, ROLE_ANALISTA, ROLE_LEITURA])
        if getattr(view, "action", None) in {"destroy"}:
            return False
        return user_in_groups(user, [ROLE_CADASTRADOR, ROLE_ANALISTA])


class SensitiveSupplierDataPermission(SupplierAPIPermission):
    """Blocks read-only users from sensitive resources such as bank data."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        user = request.user
        return can_view_sensitive_supplier_data(user)


class AdminRolePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_superuser or user_in_groups(user, [ROLE_ADMIN])))
