SUPPLIER_STATUS_CHOICES = [
    ("ATIVO", "Ativo"),
    ("INATIVO", "Inativo"),
    ("PENDENTE", "Pendente"),
    ("BLOQUEADO", "Bloqueado"),
]

SUPPLIER_PERSON_TYPE_CHOICES = [
    ("PF", "Pessoa fisica"),
    ("PJ", "Pessoa juridica"),
]

DOCUMENT_STATUS_CHOICES = [
    ("VALIDO", "Valido"),
    ("VENCIDO", "Vencido"),
    ("PENDENTE", "Pendente"),
    ("RECUSADO", "Recusado"),
]

DOCUMENT_TYPE_CHOICES = [
    ("CONTRATO_SOCIAL", "Contrato social"),
    ("CARTAO_CNPJ", "Cartao CNPJ"),
    ("CERTIDAO_NEGATIVA", "Certidao negativa"),
    ("COMPROVANTE_BANCARIO", "Comprovante bancario"),
    ("COMPROVANTE_ENDERECO", "Comprovante de endereco"),
    ("ALVARA_LICENCA", "Alvara/licenca"),
    ("OUTRO", "Outro"),
]

BANK_ACCOUNT_VALIDATION_STATUS_CHOICES = [
    ("PENDENTE", "Pendente"),
    ("VALIDADO", "Validado"),
    ("RECUSADO", "Recusado"),
]

BANK_ACCOUNT_TYPE_CHOICES = [
    ("CORRENTE", "Conta corrente"),
    ("POUPANCA", "Conta poupanca"),
    ("PAGAMENTO", "Conta pagamento"),
]
