import re
from datetime import date

from django.core.exceptions import ValidationError


ONLY_DIGITS = re.compile(r"\D+")


def only_digits(value):
    return ONLY_DIGITS.sub("", value or "")


def validate_cpf(value):
    cpf = only_digits(value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError("CPF invalido.")

    for size in (9, 10):
        total = sum(int(cpf[index]) * (size + 1 - index) for index in range(size))
        digit = (total * 10) % 11
        digit = 0 if digit == 10 else digit
        if digit != int(cpf[size]):
            raise ValidationError("CPF invalido.")


def validate_cnpj(value):
    cnpj = only_digits(value)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        raise ValidationError("CNPJ invalido.")

    weights = ((5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2), (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))
    for position, weight in enumerate(weights, start=12):
        total = sum(int(digit) * factor for digit, factor in zip(cnpj[:position], weight))
        remainder = total % 11
        expected = 0 if remainder < 2 else 11 - remainder
        if expected != int(cnpj[position]):
            raise ValidationError("CNPJ invalido.")


def validate_cpf_cnpj(value):
    digits = only_digits(value)
    if len(digits) == 11:
        validate_cpf(digits)
    elif len(digits) == 14:
        validate_cnpj(digits)
    else:
        raise ValidationError("Informe um CPF com 11 digitos ou CNPJ com 14 digitos.")


def validate_cep(value):
    if len(only_digits(value)) != 8:
        raise ValidationError("CEP deve conter 8 digitos.")


def validate_not_expired(value):
    if value and value < date.today():
        raise ValidationError("A data de validade nao pode estar vencida no cadastro inicial.")
