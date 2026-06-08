from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Fornecedor


def login_view(request):
    """Mostra a tela de login e autentica o usuario."""
    if request.user.is_authenticated:
        return redirect("listar_fornecedores")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            return redirect("listar_fornecedores")

        messages.error(request, "Usuario ou senha invalidos.")

    return render(request, "login.html")


def logout_view(request):
    """Encerra a sessao do usuario."""
    logout(request)
    return redirect("login")


@login_required
def listar_fornecedores(request):
    """Lista fornecedores e aplica busca por texto quando informada."""
    busca = request.GET.get("busca", "")
    fornecedores = Fornecedor.objects.all().order_by("nome_empresa")

    if busca:
        fornecedores = fornecedores.filter(
            Q(nome_empresa__icontains=busca)
            | Q(cnpj__icontains=busca)
            | Q(categoria__icontains=busca)
            | Q(cidade__icontains=busca)
        )

    return render(
        request,
        "listarFornecedores.html",
        {"fornecedores": fornecedores, "busca": busca},
    )


@login_required
def cadastro_fornecedor(request):
    """Cadastra um novo fornecedor no banco de dados."""
    if request.method == "POST":
        Fornecedor.objects.create(
            nome_empresa=request.POST.get("nome_empresa"),
            cnpj=request.POST.get("cnpj"),
            telefone=request.POST.get("telefone"),
            email=request.POST.get("email"),
            endereco=request.POST.get("endereco"),
            cidade=request.POST.get("cidade"),
            estado=request.POST.get("estado"),
            categoria=request.POST.get("categoria"),
            ativo=request.POST.get("ativo") == "on",
        )
        messages.success(request, "Fornecedor cadastrado com sucesso.")
        return redirect("listar_fornecedores")

    return render(request, "cadastroFornecedor.html")


@login_required
def editar_fornecedor(request, id):
    """Edita os dados de um fornecedor existente."""
    fornecedor = get_object_or_404(Fornecedor, id=id)

    if request.method == "POST":
        fornecedor.nome_empresa = request.POST.get("nome_empresa")
        fornecedor.cnpj = request.POST.get("cnpj")
        fornecedor.telefone = request.POST.get("telefone")
        fornecedor.email = request.POST.get("email")
        fornecedor.endereco = request.POST.get("endereco")
        fornecedor.cidade = request.POST.get("cidade")
        fornecedor.estado = request.POST.get("estado")
        fornecedor.categoria = request.POST.get("categoria")
        fornecedor.ativo = request.POST.get("ativo") == "on"
        fornecedor.save()

        messages.success(request, "Fornecedor atualizado com sucesso.")
        return redirect("listar_fornecedores")

    return render(request, "editarFornecedor.html", {"fornecedor": fornecedor})


@login_required
def excluir_fornecedor(request, id):
    """Exclui um fornecedor pelo id e volta para a listagem."""
    fornecedor = get_object_or_404(Fornecedor, id=id)
    fornecedor.delete()
    messages.success(request, "Fornecedor excluido com sucesso.")
    return redirect("listar_fornecedores")
