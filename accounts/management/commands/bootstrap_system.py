import os

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q

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
    help = "Creates default roles, categories and optional deploy superuser."

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

        self.create_deploy_superuser()

        self.stdout.write(self.style.SUCCESS("Default roles and categories are ready."))

    def create_deploy_superuser(self):
        username = (os.environ.get("DJANGO_SUPERUSER_USERNAME") or "").strip()
        email = (os.environ.get("DJANGO_SUPERUSER_EMAIL") or "").strip()
        password = (os.environ.get("DJANGO_SUPERUSER_PASSWORD") or "").strip()

        if not username or not password:
            self.stdout.write("Deploy superuser skipped: DJANGO_SUPERUSER_USERNAME/PASSWORD not set.")
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        changed_fields = []
        if not user.is_staff:
            user.is_staff = True
            changed_fields.append("is_staff")
        if not user.is_superuser:
            user.is_superuser = True
            changed_fields.append("is_superuser")
        if email and user.email != email:
            user.email = email
            changed_fields.append("email")

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Deploy superuser '{username}' created."))
            return

        user.set_password(password)
        changed_fields.append("password")

        if changed_fields:
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Deploy superuser '{username}' updated."))
        else:
            self.stdout.write(f"Deploy superuser '{username}' already exists.")
