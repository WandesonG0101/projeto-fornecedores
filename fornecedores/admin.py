from django.contrib import admin

from .models import Fornecedor


# Permite gerenciar fornecedores pela area administrativa do Django.
@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = (
        "nome_empresa",
        "cnpj",
        "telefone",
        "email",
        "cidade",
        "estado",
        "categoria",
        "ativo",
    )
    search_fields = ("nome_empresa", "cnpj", "cidade", "categoria")
    list_filter = ("ativo", "estado", "categoria")
