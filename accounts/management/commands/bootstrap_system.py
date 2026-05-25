from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from django.core.management.base import BaseCommand

from core.permissions import ROLE_ADMIN, ROLE_ANALISTA, ROLE_CADASTRADOR, ROLE_LEITURA
from suppliers.models import SupplierCategory


DEFAULT_CATEGORIES = [
    "Material de consumo",
    "Equipamentos",
    "Servicos laboratoriais",
    "Manutencao",
    "Obras e reformas",
    "Tecnologia da informacao",
    "Servicos terceirizados",
    "Outros",
]


class Command(BaseCommand):
    help = "Creates default API roles and supplier categories."

    def handle(self, *args, **options):
        all_permissions = Permission.objects.all()
        view_permissions = Permission.objects.filter(codename__startswith="view_")
        change_permissions = Permission.objects.filter(
            Q(codename__startswith="view_") | Q(codename__startswith="add_") | Q(codename__startswith="change_")
        )

        role_map = {
            ROLE_ADMIN: all_permissions,
            ROLE_CADASTRADOR: change_permissions,
            ROLE_ANALISTA: change_permissions,
            ROLE_LEITURA: view_permissions,
        }

        for role, permissions in role_map.items():
            group, _ = Group.objects.get_or_create(name=role)
            group.permissions.set(permissions)

        for category in DEFAULT_CATEGORIES:
            SupplierCategory.objects.get_or_create(name=category)

        self.stdout.write(self.style.SUCCESS("Default roles and categories are ready."))
