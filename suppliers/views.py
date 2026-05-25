from django.db.models import Prefetch
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import SensitiveSupplierDataPermission, SupplierAPIPermission, can_view_sensitive_supplier_data
from documents.models import SupplierDocument
from documents.serializers import SupplierDocumentSerializer
from suppliers.models import BankAccount, Supplier, SupplierCategory, SupplierContact
from suppliers.serializers import (
    BankAccountSerializer,
    SupplierCategorySerializer,
    SupplierContactSerializer,
    SupplierListSerializer,
    SupplierSerializer,
)


class SupplierCategoryViewSet(viewsets.ModelViewSet):
    queryset = SupplierCategory.objects.all()
    serializer_class = SupplierCategorySerializer
    permission_classes = [SupplierAPIPermission]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]


class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [SupplierAPIPermission]
    filterset_fields = ["status", "category", "person_type", "city", "state"]
    search_fields = ["legal_name", "trade_name", "tax_id", "city", "category__name"]
    ordering_fields = ["legal_name", "created_at", "updated_at"]

    def get_queryset(self):
        queryset = Supplier.objects.select_related("category").prefetch_related(
            "contacts",
            Prefetch("documents", queryset=SupplierDocument.objects.order_by("-uploaded_at")),
        )
        if can_view_sensitive_supplier_data(self.request.user):
            queryset = queryset.prefetch_related("bank_accounts")
        return queryset.all()

    def get_serializer_class(self):
        if self.action == "list":
            return SupplierListSerializer
        return SupplierSerializer

    def get_search_fields(self):
        if can_view_sensitive_supplier_data(self.request.user):
            return self.search_fields
        return ["legal_name", "trade_name", "city", "category__name"]

    def get_filterset_fields(self):
        if can_view_sensitive_supplier_data(self.request.user):
            return self.filterset_fields
        return ["status", "category", "person_type", "city", "state"]

    @action(detail=True, methods=["post"], url_path="inativar")
    def inactivate(self, request, pk=None):
        supplier = self.get_object()
        supplier.inactivate()
        serializer = self.get_serializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="por-categoria/(?P<category_id>[^/.]+)")
    def by_category(self, request, category_id=None):
        queryset = self.filter_queryset(self.get_queryset().filter(category_id=category_id))
        page = self.paginate_queryset(queryset)
        serializer = SupplierListSerializer(page or queryset, many=True, context={"request": request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post"], url_path="documentos")
    def documents(self, request, pk=None):
        supplier = self.get_object()
        if request.method == "GET":
            serializer = SupplierDocumentSerializer(supplier.documents.order_by("-uploaded_at"), many=True, context={"request": request})
            return Response(serializer.data)

        data = request.data.copy()
        data["supplier"] = supplier.pk
        serializer = SupplierDocumentSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SupplierContactViewSet(viewsets.ModelViewSet):
    queryset = SupplierContact.objects.select_related("supplier").all()
    serializer_class = SupplierContactSerializer
    permission_classes = [SupplierAPIPermission]
    filterset_fields = ["supplier"]
    search_fields = ["name", "email", "supplier__legal_name"]
    ordering_fields = ["name", "created_at"]

    def get_search_fields(self):
        if can_view_sensitive_supplier_data(self.request.user):
            return self.search_fields
        return ["name", "supplier__legal_name"]


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.select_related("supplier").all()
    serializer_class = BankAccountSerializer
    permission_classes = [SensitiveSupplierDataPermission]
    filterset_fields = ["supplier", "validation_status", "account_type"]
    search_fields = ["supplier__legal_name", "holder_name", "holder_tax_id", "bank"]
    ordering_fields = ["bank", "created_at"]
