from django.urls import path

from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("listarfornecedores/", views.listar_fornecedores, name="listar_fornecedores"),
    path("cadastrofornecedor/", views.cadastro_fornecedor, name="cadastro_fornecedor"),
    path("editarfornecedor/<int:id>/", views.editar_fornecedor, name="editar_fornecedor"),
    path("excluirfornecedor/<int:id>/", views.excluir_fornecedor, name="excluir_fornecedor"),
]
