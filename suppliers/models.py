from django.core.exceptions import ValidationError
from django.db import models

from core.models import TimeStampedModel
from core.validators import only_digits, validate_cep, validate_cnpj, validate_cpf, validate_cpf_cnpj


class SupplierCategory(TimeStampedModel):
    name = models.CharField("nome", max_length=120, unique=True)
    description = models.TextField("descricao", blank=True)
    is_active = models.BooleanField("ativa", default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria de fornecedor"
        verbose_name_plural = "categorias de fornecedores"

    def __str__(self):
        return self.name


class Supplier(TimeStampedModel):
    class PersonType(models.TextChoices):
        INDIVIDUAL = "PF", "Pessoa fisica"
        COMPANY = "PJ", "Pessoa juridica"

    class Status(models.TextChoices):
        ACTIVE = "ATIVO", "Ativo"
        INACTIVE = "INATIVO", "Inativo"
        PENDING = "PENDENTE", "Pendente"
        BLOCKED = "BLOQUEADO", "Bloqueado"

    person_type = models.CharField("tipo de pessoa", max_length=2, choices=PersonType.choices)
    legal_name = models.CharField("nome/razao social", max_length=255)
    trade_name = models.CharField("nome fantasia", max_length=255, blank=True)
    tax_id = models.CharField("CPF/CNPJ", max_length=14, unique=True, validators=[validate_cpf_cnpj])
    state_registration = models.CharField("inscricao estadual", max_length=50, blank=True)
    municipal_registration = models.CharField("inscricao municipal", max_length=50, blank=True)
    email = models.EmailField("e-mail")
    phone = models.CharField("telefone", max_length=30, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=30, blank=True)
    zip_code = models.CharField("CEP", max_length=8, validators=[validate_cep])
    street = models.CharField("logradouro", max_length=255)
    number = models.CharField("numero", max_length=30)
    complement = models.CharField("complemento", max_length=120, blank=True)
    district = models.CharField("bairro", max_length=120)
    city = models.CharField("cidade", max_length=120)
    state = models.CharField("estado", max_length=2)
    country = models.CharField("pais", max_length=80, default="Brasil")
    category = models.ForeignKey(
        SupplierCategory,
        verbose_name="categoria",
        related_name="suppliers",
        on_delete=models.PROTECT,
    )
    products_services = models.TextField("produtos ou servicos fornecidos")
    status = models.CharField("situacao cadastral", max_length=10, choices=Status.choices, default=Status.PENDING)
    internal_notes = models.TextField("observacoes internas", blank=True)

    class Meta:
        ordering = ["legal_name"]
        verbose_name = "fornecedor"
        verbose_name_plural = "fornecedores"
        indexes = [
            models.Index(fields=["tax_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["city"]),
        ]

    def __str__(self):
        return self.legal_name

    def clean(self):
        super().clean()
        digits = only_digits(self.tax_id)
        if self.person_type == self.PersonType.INDIVIDUAL and len(digits) == 14:
            raise ValidationError({"tax_id": "Pessoa fisica deve usar CPF."})
        if self.person_type == self.PersonType.COMPANY and len(digits) == 11:
            raise ValidationError({"tax_id": "Pessoa juridica deve usar CNPJ."})
        if self.person_type == self.PersonType.INDIVIDUAL:
            validate_cpf(digits)
        else:
            validate_cnpj(digits)

    def save(self, *args, **kwargs):
        self.tax_id = only_digits(self.tax_id)
        self.zip_code = only_digits(self.zip_code)
        self.state = (self.state or "").upper()
        self.full_clean()
        super().save(*args, **kwargs)

    def inactivate(self):
        self.status = self.Status.INACTIVE
        self.save(update_fields=["status", "updated_at"])


class SupplierContact(TimeStampedModel):
    supplier = models.ForeignKey(Supplier, related_name="contacts", on_delete=models.CASCADE)
    name = models.CharField("nome do contato", max_length=150)
    role = models.CharField("cargo/funcao", max_length=120, blank=True)
    email = models.EmailField("e-mail", blank=True)
    phone = models.CharField("telefone", max_length=30, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=30, blank=True)
    notes = models.TextField("observacoes", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "contato do fornecedor"
        verbose_name_plural = "contatos dos fornecedores"

    def __str__(self):
        return f"{self.name} - {self.supplier}"


class BankAccount(TimeStampedModel):
    class AccountType(models.TextChoices):
        CHECKING = "CORRENTE", "Conta corrente"
        SAVINGS = "POUPANCA", "Conta poupanca"
        PAYMENT = "PAGAMENTO", "Conta pagamento"

    class ValidationStatus(models.TextChoices):
        PENDING = "PENDENTE", "Pendente"
        VALIDATED = "VALIDADO", "Validado"
        REJECTED = "RECUSADO", "Recusado"

    supplier = models.ForeignKey(Supplier, related_name="bank_accounts", on_delete=models.CASCADE)
    bank = models.CharField("banco", max_length=120)
    branch = models.CharField("agencia", max_length=20)
    account = models.CharField("conta", max_length=30)
    account_type = models.CharField("tipo de conta", max_length=20, choices=AccountType.choices)
    pix_key = models.CharField("chave PIX", max_length=120, blank=True)
    holder_name = models.CharField("titular da conta", max_length=150)
    holder_tax_id = models.CharField("CPF/CNPJ do titular", max_length=14, validators=[validate_cpf_cnpj])
    validation_status = models.CharField(
        "status de validacao",
        max_length=10,
        choices=ValidationStatus.choices,
        default=ValidationStatus.PENDING,
    )

    class Meta:
        ordering = ["bank", "branch", "account"]
        verbose_name = "dado bancario"
        verbose_name_plural = "dados bancarios"

    def __str__(self):
        return f"{self.bank} - {self.branch}/{self.account}"

    def save(self, *args, **kwargs):
        self.holder_tax_id = only_digits(self.holder_tax_id)
        self.full_clean()
        super().save(*args, **kwargs)
