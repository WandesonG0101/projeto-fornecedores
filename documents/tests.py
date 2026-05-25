import shutil
from pathlib import Path

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from core.permissions import ROLE_ANALISTA, ROLE_CADASTRADOR
from documents.models import SupplierDocument
from suppliers.models import Supplier, SupplierCategory


TEST_MEDIA_ROOT = Path(__file__).resolve().parent.parent / "test_media"


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class SupplierDocumentAPITests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.category = SupplierCategory.objects.create(name="Material de consumo")
        self.supplier = Supplier.objects.create(
            person_type="PJ",
            legal_name="Fornecedor Documento Ltda",
            trade_name="Fornecedor Documento",
            tax_id="11222333000181",
            email="documentos@example.com",
            zip_code="01001000",
            street="Rua Central",
            number="1",
            district="Centro",
            city="Sao Paulo",
            state="SP",
            category=self.category,
            products_services="Materiais",
        )
        self.user = User.objects.create_user(username="docs", password="pass12345")
        self.analyst = User.objects.create_user(username="analyst-docs", password="pass12345")
        group = Group.objects.create(name=ROLE_CADASTRADOR)
        analyst_group = Group.objects.create(name=ROLE_ANALISTA)
        self.user.groups.add(group)
        self.analyst.groups.add(analyst_group)

    def test_upload_supplier_document(self):
        self.client.force_authenticate(self.user)
        upload = SimpleUploadedFile("cnpj.pdf", b"fake-pdf-content", content_type="application/pdf")

        response = self.client.post(
            f"/api/v1/fornecedores/{self.supplier.id}/documentos/",
            {
                "document_type": "CARTAO_CNPJ",
                "file": upload,
                "status": "PENDENTE",
                "analysis_note": "Aguardando analise.",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.supplier.documents.count(), 1)

    def test_expired_document_cannot_be_valid(self):
        self.client.force_authenticate(self.user)
        upload = SimpleUploadedFile("certidao.pdf", b"fake-pdf-content", content_type="application/pdf")

        response = self.client.post(
            "/api/v1/documentos/",
            {
                "supplier": self.supplier.id,
                "document_type": "CERTIDAO_NEGATIVA",
                "file": upload,
                "expires_at": "2000-01-01",
                "status": "VALIDO",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_document_extension_is_rejected(self):
        self.client.force_authenticate(self.user)
        upload = SimpleUploadedFile("script.exe", b"fake-content", content_type="application/octet-stream")

        response = self.client.post(
            "/api/v1/documentos/",
            {
                "supplier": self.supplier.id,
                "document_type": "OUTRO",
                "file": upload,
                "status": "PENDENTE",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creator_cannot_mark_document_as_valid(self):
        document = SupplierDocument.objects.create(
            supplier=self.supplier,
            document_type="CARTAO_CNPJ",
            file=SimpleUploadedFile("cnpj.pdf", b"fake-pdf-content", content_type="application/pdf"),
            status="PENDENTE",
        )
        self.client.force_authenticate(self.user)

        response = self.client.patch(f"/api/v1/documentos/{document.id}/", {"status": "VALIDO"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_analyst_can_mark_document_as_valid(self):
        document = SupplierDocument.objects.create(
            supplier=self.supplier,
            document_type="CARTAO_CNPJ",
            file=SimpleUploadedFile("cnpj.pdf", b"fake-pdf-content", content_type="application/pdf"),
            status="PENDENTE",
        )
        self.client.force_authenticate(self.analyst)

        response = self.client.patch(f"/api/v1/documentos/{document.id}/", {"status": "VALIDO"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        document.refresh_from_db()
        self.assertEqual(document.status, "VALIDO")
