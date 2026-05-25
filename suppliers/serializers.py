from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from core.permissions import can_analyze_supplier_data, can_view_sensitive_supplier_data
from core.validators import only_digits, validate_cep, validate_cpf_cnpj
from suppliers.models import BankAccount, Supplier, SupplierCategory, SupplierContact


class SupplierCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierCategory
        fields = ["id", "name", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierContact
        fields = ["id", "supplier", "name", "role", "email", "phone", "whatsapp", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierNestedContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierContact
        fields = ["id", "name", "role", "email", "phone", "whatsapp", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class BankAccountSerializer(serializers.ModelSerializer):
    holder_tax_id = serializers.CharField(validators=[validate_cpf_cnpj])

    class Meta:
        model = BankAccount
        fields = [
            "id",
            "supplier",
            "bank",
            "branch",
            "account",
            "account_type",
            "pix_key",
            "holder_name",
            "holder_tax_id",
            "validation_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_holder_tax_id(self, value):
        return only_digits(value)

    def validate(self, attrs):
        request = self.context.get("request")
        new_status = attrs.get("validation_status")
        current_status = getattr(self.instance, "validation_status", None)
        status_changed = new_status and new_status != current_status
        if status_changed and new_status != BankAccount.ValidationStatus.PENDING:
            if not request or not can_analyze_supplier_data(request.user):
                raise serializers.ValidationError({"validation_status": "Somente analistas ou administradores podem validar dados bancarios."})
        return attrs


class NestedBankAccountSerializer(BankAccountSerializer):
    class Meta(BankAccountSerializer.Meta):
        fields = [
            "id",
            "bank",
            "branch",
            "account",
            "account_type",
            "pix_key",
            "holder_name",
            "holder_tax_id",
            "validation_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SupplierListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Supplier
        fields = ["id", "legal_name", "trade_name", "tax_id", "person_type", "category", "category_name", "city", "state", "status"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and not can_view_sensitive_supplier_data(request.user):
            data.pop("tax_id", None)
        return data


class SupplierSerializer(serializers.ModelSerializer):
    tax_id = serializers.CharField(validators=[validate_cpf_cnpj])
    zip_code = serializers.CharField(validators=[validate_cep])
    contacts = SupplierNestedContactSerializer(many=True, required=False)
    bank_accounts = NestedBankAccountSerializer(many=True, required=False)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Supplier
        fields = [
            "id",
            "person_type",
            "legal_name",
            "trade_name",
            "tax_id",
            "state_registration",
            "municipal_registration",
            "email",
            "phone",
            "whatsapp",
            "zip_code",
            "street",
            "number",
            "complement",
            "district",
            "city",
            "state",
            "country",
            "category",
            "category_name",
            "products_services",
            "status",
            "internal_notes",
            "contacts",
            "bank_accounts",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_tax_id(self, value):
        digits = only_digits(value)
        queryset = Supplier.objects.filter(tax_id=digits)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Ja existe fornecedor cadastrado com este CPF/CNPJ.")
        return digits

    def validate_zip_code(self, value):
        return only_digits(value)

    def validate(self, attrs):
        request = self.context.get("request")
        new_status = attrs.get("status")
        current_status = getattr(self.instance, "status", None)
        status_changed = new_status and new_status != current_status
        if status_changed and new_status in {Supplier.Status.ACTIVE, Supplier.Status.BLOCKED}:
            if not request or not can_analyze_supplier_data(request.user):
                raise serializers.ValidationError({"status": "Somente analistas ou administradores podem ativar ou bloquear fornecedores."})

        model_fields = {field.name for field in Supplier._meta.fields}
        data = {}
        if self.instance:
            for field in model_fields:
                if hasattr(self.instance, field):
                    data[field] = getattr(self.instance, field)
        data.update(attrs)
        supplier = Supplier(**{key: value for key, value in data.items() if key in model_fields})
        try:
            supplier.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(getattr(exc, "message_dict", str(exc)))
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and not can_view_sensitive_supplier_data(request.user):
            data.pop("tax_id", None)
            data.pop("internal_notes", None)
            data.pop("bank_accounts", None)
        return data

    @transaction.atomic
    def create(self, validated_data):
        contacts = validated_data.pop("contacts", [])
        bank_accounts = validated_data.pop("bank_accounts", [])
        supplier = Supplier.objects.create(**validated_data)
        for contact in contacts:
            contact.pop("supplier", None)
            SupplierContact.objects.create(supplier=supplier, **contact)
        for account in bank_accounts:
            account.pop("supplier", None)
            BankAccount.objects.create(supplier=supplier, **account)
        return supplier

    def update(self, instance, validated_data):
        validated_data.pop("contacts", None)
        validated_data.pop("bank_accounts", None)
        return super().update(instance, validated_data)
