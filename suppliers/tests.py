from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.test import APITestCase

from core.permissions import ROLE_ADMIN, ROLE_ANALISTA, ROLE_CADASTRADOR, ROLE_LEITURA
from integrations.models import IntegrationLog
from suppliers.models import BankAccount, Supplier, SupplierCategory


class SupplierAPITests(APITestCase):
    def setUp(self):
        self.category = SupplierCategory.objects.create(name="Tecnologia da informacao")
        self.creator = User.objects.create_user(username="creator", password="pass12345")
        self.reader = User.objects.create_user(username="reader", password="pass12345")
        self.analyst = User.objects.create_user(username="analyst", password="pass12345")
        self.admin_user = User.objects.create_user(username="admin-role", password="pass12345")
        creator_group = Group.objects.create(name=ROLE_CADASTRADOR)
        reader_group = Group.objects.create(name=ROLE_LEITURA)
        analyst_group = Group.objects.create(name=ROLE_ANALISTA)
        admin_group = Group.objects.create(name=ROLE_ADMIN)
        self.creator.groups.add(creator_group)
        self.reader.groups.add(reader_group)
        self.analyst.groups.add(analyst_group)
        self.admin_user.groups.add(admin_group)

    def supplier_payload(self, tax_id="11222333000181"):
        return {
            "person_type": "PJ",
            "legal_name": "Fornecedor Exemplo Ltda",
            "trade_name": "Fornecedor Exemplo",
            "tax_id": tax_id,
            "email": "contato@example.com",
            "phone": "1133334444",
            "whatsapp": "11999998888",
            "zip_code": "01001000",
            "street": "Praca da Se",
            "number": "100",
            "district": "Se",
            "city": "Sao Paulo",
            "state": "SP",
            "country": "Brasil",
            "category": self.category.id,
            "products_services": "Sistemas corporativos e suporte tecnico",
            "status": "PENDENTE",
        }

    def test_create_supplier(self):
        self.client.force_authenticate(self.creator)
        response = self.client.post("/api/v1/fornecedores/", self.supplier_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 1)
        self.assertEqual(Supplier.objects.get().tax_id, "11222333000181")

    def test_duplicate_tax_id_is_rejected(self):
        self.client.force_authenticate(self.creator)
        response = self.client.post("/api/v1/fornecedores/", self.supplier_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        duplicate = self.client.post("/api/v1/fornecedores/", self.supplier_payload(), format="json")
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_suppliers(self):
        payload = self.supplier_payload()
        payload["category"] = self.category
        Supplier.objects.create(**payload)
        self.client.force_authenticate(self.reader)

        response = self.client.get("/api/v1/fornecedores/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["results"])

    def test_read_only_supplier_response_hides_sensitive_fields(self):
        payload = self.supplier_payload()
        payload["category"] = self.category
        supplier = Supplier.objects.create(**payload)
        BankAccount.objects.create(
            supplier=supplier,
            bank="Banco Exemplo",
            branch="0001",
            account="12345-6",
            account_type="CORRENTE",
            holder_name="Fornecedor Exemplo Ltda",
            holder_tax_id="11222333000181",
        )
        self.client.force_authenticate(self.reader)

        response = self.client.get(f"/api/v1/fornecedores/{supplier.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("tax_id", response.data)
        self.assertNotIn("internal_notes", response.data)
        self.assertNotIn("bank_accounts", response.data)

    def test_read_only_user_cannot_create_supplier(self):
        self.client.force_authenticate(self.reader)
        response = self.client.post("/api/v1/fornecedores/", self.supplier_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_creator_cannot_activate_supplier(self):
        payload = self.supplier_payload()
        payload["category"] = self.category
        supplier = Supplier.objects.create(**payload)
        self.client.force_authenticate(self.creator)

        response = self.client.patch(f"/api/v1/fornecedores/{supplier.id}/", {"status": "ATIVO"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_analyst_can_activate_supplier(self):
        payload = self.supplier_payload()
        payload["category"] = self.category
        supplier = Supplier.objects.create(**payload)
        self.client.force_authenticate(self.analyst)

        response = self.client.patch(f"/api/v1/fornecedores/{supplier.id}/", {"status": "ATIVO"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        supplier.refresh_from_db()
        self.assertEqual(supplier.status, "ATIVO")

    def test_read_only_user_cannot_access_bank_accounts(self):
        payload = self.supplier_payload()
        payload["category"] = self.category
        supplier = Supplier.objects.create(**payload)
        BankAccount.objects.create(
            supplier=supplier,
            bank="Banco Exemplo",
            branch="0001",
            account="12345-6",
            account_type="CORRENTE",
            holder_name="Fornecedor Exemplo Ltda",
            holder_tax_id="11222333000181",
        )
        self.client.force_authenticate(self.reader)

        response = self.client.get("/api/v1/dados-bancarios/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_integration_logs_are_admin_only(self):
        IntegrationLog.objects.create(
            source_system="fornecedores",
            target_system="financeiro",
            endpoint="https://example.com/api",
            http_method="POST",
            request_status=200,
        )
        self.client.force_authenticate(self.reader)
        reader_response = self.client.get("/api/v1/integracoes/logs/")
        self.assertEqual(reader_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin_user)
        admin_response = self.client.get("/api/v1/integracoes/logs/")
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_response.data["results"][0]["target_system"], "financeiro")
