from django.urls import include, path
from rest_framework.routers import DefaultRouter

from documents.views import SupplierDocumentViewSet
from integrations.views import IntegrationLogViewSet
from suppliers.views import BankAccountViewSet, SupplierCategoryViewSet, SupplierContactViewSet, SupplierViewSet


router = DefaultRouter()
router.register("categorias", SupplierCategoryViewSet, basename="categoria")
router.register("fornecedores", SupplierViewSet, basename="fornecedor")
router.register("contatos", SupplierContactViewSet, basename="contato")
router.register("dados-bancarios", BankAccountViewSet, basename="dado-bancario")
router.register("documentos", SupplierDocumentViewSet, basename="documento")
router.register("integracoes/logs", IntegrationLogViewSet, basename="integracao-log")

urlpatterns = [
    path("", include(router.urls)),
]
