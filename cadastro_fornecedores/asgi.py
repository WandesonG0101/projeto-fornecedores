"""Configuracao ASGI do projeto cadastro_fornecedores."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cadastro_fornecedores.settings")

application = get_asgi_application()
