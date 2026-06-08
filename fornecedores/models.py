from django.db import models


class Fornecedor(models.Model):
    """Tabela que guarda os dados principais dos fornecedores."""

    nome_empresa = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=18)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    endereco = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    categoria = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_empresa
