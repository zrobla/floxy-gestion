from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from integrations.models import LoyverseReceipt
from operations.models import Activity, ActivityLine, PaymentLink, Service
from operations.serializers import (
    ActivityLineSerializer,
    ActivitySerializer,
    PaymentLinkSerializer,
    ServiceSerializer,
)

User = get_user_model()


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class ActivityLineViewSet(viewsets.ModelViewSet):
    queryset = ActivityLine.objects.select_related("activity", "service")
    serializer_class = ActivityLineSerializer


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.select_related("assigned_staff")
    serializer_class = ActivitySerializer

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        activity = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            raise DRFValidationError({"status": "Le statut est obligatoire."})
        try:
            activity.set_status(new_status)
        except ValidationError as exc:
            raise DRFValidationError(exc.message_dict or {"detail": str(exc)}) from exc
        serializer = self.get_serializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def mark_done(self, request, pk=None):
        activity = self.get_object()
        try:
            activity.set_status(Activity.Status.DONE, save=False)
        except ValidationError as exc:
            raise DRFValidationError({"detail": str(exc)}) from exc
        activity.end_at = activity.end_at or timezone.now()
        activity.save(update_fields=["status", "end_at", "updated_at"])
        serializer = self.get_serializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def assign_staff(self, request, pk=None):
        activity = self.get_object()
        staff_id = request.data.get("staff_id")
        if not staff_id:
            raise DRFValidationError({"staff_id": "Le collaborateur est obligatoire."})
        staff = get_object_or_404(User, pk=staff_id)
        activity.assigned_staff = staff
        activity.save(update_fields=["assigned_staff", "updated_at"])
        serializer = self.get_serializer(activity)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def link_payment(self, request, pk=None):
        activity = self.get_object()
        if request.user.role not in {"MANAGER", "ADMIN"}:
            raise DRFValidationError({"detail": "Accès réservé aux gestionnaires."})

        serializer = PaymentLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receipt_id = serializer.validated_data.get("receipt_id")
        manual_reference = serializer.validated_data.get("manual_reference", "").strip()
        final_amount = serializer.validated_data.get("final_amount")

        if not receipt_id and not manual_reference:
            raise DRFValidationError(
                {"detail": "Une référence manuelle ou un reçu Loyverse est requis."}
            )

        loyverse_receipt = None
        if receipt_id:
            loyverse_receipt = LoyverseReceipt.objects.filter(pk=receipt_id).first()
            if not loyverse_receipt:
                raise DRFValidationError({"receipt_id": "Reçu Loyverse introuvable."})

        payment_link, _ = PaymentLink.objects.update_or_create(
            activity=activity,
            defaults={
                "loyverse_receipt": loyverse_receipt,
                "manual_reference": manual_reference,
            },
        )

        if activity.status == Activity.Status.DONE:
            activity.status = Activity.Status.TO_COLLECT
        if activity.status == Activity.Status.TO_COLLECT:
            activity.status = Activity.Status.PAID
        elif activity.status != Activity.Status.PAID:
            raise DRFValidationError(
                {"detail": "Le statut doit être terminé ou à encaisser."}
            )

        if final_amount is not None:
            activity.final_amount = final_amount
        elif activity.final_amount is None:
            activity.final_amount = activity.expected_amount

        activity.save(update_fields=["status", "final_amount", "updated_at"])

        return Response(
            {
                "id": payment_link.id,
                "activity": activity.id,
                "status": activity.status,
                "final_amount": str(activity.final_amount),
            },
            status=status.HTTP_200_OK,
        )
