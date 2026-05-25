# Generated manually for the initial supplier domain schema.
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SupplierCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="data de criacao")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="data de atualizacao")),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="nome")),
                ("description", models.TextField(blank=True, verbose_name="descricao")),
                ("is_active", models.BooleanField(default=True, verbose_name="ativa")),
            ],
            options={
                "verbose_name": "categoria de fornecedor",
                "verbose_name_plural": "categorias de fornecedores",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="data de criacao")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="data de atualizacao")),
                ("person_type", models.CharField(choices=[("PF", "Pessoa fisica"), ("PJ", "Pessoa juridica")], max_length=2, verbose_name="tipo de pessoa")),
                ("legal_name", models.CharField(max_length=255, verbose_name="nome/razao social")),
                ("trade_name", models.CharField(blank=True, max_length=255, verbose_name="nome fantasia")),
                ("tax_id", models.CharField(max_length=14, unique=True, validators=[core.validators.validate_cpf_cnpj], verbose_name="CPF/CNPJ")),
                ("state_registration", models.CharField(blank=True, max_length=50, verbose_name="inscricao estadual")),
                ("municipal_registration", models.CharField(blank=True, max_length=50, verbose_name="inscricao municipal")),
                ("email", models.EmailField(max_length=254, verbose_name="e-mail")),
                ("phone", models.CharField(blank=True, max_length=30, verbose_name="telefone")),
                ("whatsapp", models.CharField(blank=True, max_length=30, verbose_name="WhatsApp")),
                ("zip_code", models.CharField(max_length=8, validators=[core.validators.validate_cep], verbose_name="CEP")),
                ("street", models.CharField(max_length=255, verbose_name="logradouro")),
                ("number", models.CharField(max_length=30, verbose_name="numero")),
                ("complement", models.CharField(blank=True, max_length=120, verbose_name="complemento")),
                ("district", models.CharField(max_length=120, verbose_name="bairro")),
                ("city", models.CharField(max_length=120, verbose_name="cidade")),
                ("state", models.CharField(max_length=2, verbose_name="estado")),
                ("country", models.CharField(default="Brasil", max_length=80, verbose_name="pais")),
                ("products_services", models.TextField(verbose_name="produtos ou servicos fornecidos")),
                ("status", models.CharField(choices=[("ATIVO", "Ativo"), ("INATIVO", "Inativo"), ("PENDENTE", "Pendente"), ("BLOQUEADO", "Bloqueado")], default="PENDENTE", max_length=10, verbose_name="situacao cadastral")),
                ("internal_notes", models.TextField(blank=True, verbose_name="observacoes internas")),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="suppliers", to="suppliers.suppliercategory", verbose_name="categoria")),
            ],
            options={
                "verbose_name": "fornecedor",
                "verbose_name_plural": "fornecedores",
                "ordering": ["legal_name"],
            },
        ),
        migrations.CreateModel(
            name="BankAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="data de criacao")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="data de atualizacao")),
                ("bank", models.CharField(max_length=120, verbose_name="banco")),
                ("branch", models.CharField(max_length=20, verbose_name="agencia")),
                ("account", models.CharField(max_length=30, verbose_name="conta")),
                ("account_type", models.CharField(choices=[("CORRENTE", "Conta corrente"), ("POUPANCA", "Conta poupanca"), ("PAGAMENTO", "Conta pagamento")], max_length=20, verbose_name="tipo de conta")),
                ("pix_key", models.CharField(blank=True, max_length=120, verbose_name="chave PIX")),
                ("holder_name", models.CharField(max_length=150, verbose_name="titular da conta")),
                ("holder_tax_id", models.CharField(max_length=14, validators=[core.validators.validate_cpf_cnpj], verbose_name="CPF/CNPJ do titular")),
                ("validation_status", models.CharField(choices=[("PENDENTE", "Pendente"), ("VALIDADO", "Validado"), ("RECUSADO", "Recusado")], default="PENDENTE", max_length=10, verbose_name="status de validacao")),
                ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bank_accounts", to="suppliers.supplier")),
            ],
            options={
                "verbose_name": "dado bancario",
                "verbose_name_plural": "dados bancarios",
                "ordering": ["bank", "branch", "account"],
            },
        ),
        migrations.CreateModel(
            name="SupplierContact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="data de criacao")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="data de atualizacao")),
                ("name", models.CharField(max_length=150, verbose_name="nome do contato")),
                ("role", models.CharField(blank=True, max_length=120, verbose_name="cargo/funcao")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="e-mail")),
                ("phone", models.CharField(blank=True, max_length=30, verbose_name="telefone")),
                ("whatsapp", models.CharField(blank=True, max_length=30, verbose_name="WhatsApp")),
                ("notes", models.TextField(blank=True, verbose_name="observacoes")),
                ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contacts", to="suppliers.supplier")),
            ],
            options={
                "verbose_name": "contato do fornecedor",
                "verbose_name_plural": "contatos dos fornecedores",
                "ordering": ["name"],
            },
        ),
        migrations.AddIndex(model_name="supplier", index=models.Index(fields=["tax_id"], name="suppliers_su_tax_id_32224c_idx")),
        migrations.AddIndex(model_name="supplier", index=models.Index(fields=["status"], name="suppliers_su_status_56e639_idx")),
        migrations.AddIndex(model_name="supplier", index=models.Index(fields=["city"], name="suppliers_su_city_264195_idx")),
    ]
