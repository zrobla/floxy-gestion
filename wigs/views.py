from datetime import date
from io import BytesIO

import qrcode
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError

from wigs.models import CareWig, WigProduct
from wigs.serializers import CareWigSerializer, WigProductSerializer


def parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise DRFValidationError(
            {field: "Format de date invalide. Utilisez AAAA-MM-JJ."}
        ) from exc


def apply_filters(queryset, params, search_fields):
    status = params.get("status")
    code = params.get("code")
    query = params.get("q")
    start_date = params.get("start_date")
    end_date = params.get("end_date")

    if status:
        queryset = queryset.filter(status=status)
    if code:
        queryset = queryset.filter(code__icontains=code)
    if query:
        filters = Q()
        for field in search_fields:
            filters |= Q(**{f"{field}__icontains": query})
        queryset = queryset.filter(filters)

    start_value = parse_date(start_date, "start_date") if start_date else None
    end_value = parse_date(end_date, "end_date") if end_date else None
    if start_value and end_value and start_value > end_value:
        raise DRFValidationError(
            {"end_date": "La date de fin doit être postérieure à la date de début."}
        )
    if start_value:
        queryset = queryset.filter(created_at__date__gte=start_value)
    if end_value:
        queryset = queryset.filter(created_at__date__lte=end_value)
    return queryset


def draw_logo(pdf, x: float, y: float, size: float) -> None:
    logo_path = getattr(settings, "FLOXY_LOGO_PATH", "")
    if logo_path:
        try:
            logo_reader = ImageReader(logo_path)
            pdf.drawImage(
                logo_reader,
                x,
                y,
                width=size,
                height=size,
                preserveAspectRatio=True,
                mask="auto",
            )
            return
        except Exception:
            pass

    pdf.setLineWidth(1)
    pdf.circle(x + size / 2, y + size / 2, size / 2, stroke=1, fill=0)
    pdf.setFont("Helvetica-Bold", 6)
    pdf.drawCentredString(x + size / 2, y + size / 2 - 2, "FM")


def get_client_initials(client: str) -> str:
    parts = [part for part in client.split() if part]
    if not parts:
        return "ND"
    initials = "".join(part[0] for part in parts[:2]).upper()
    return initials


def care_wig_label(request, pk: int):
    care_wig = get_object_or_404(CareWig, pk=pk)
    printed_at = timezone.localtime(timezone.now())
    promised = (
        care_wig.promised_date.strftime("%d/%m/%Y")
        if care_wig.promised_date
        else "Non définie"
    )
    initials = get_client_initials(care_wig.client)

    buffer = BytesIO()
    label_width = 80 * mm
    label_height = 50 * mm
    pdf = canvas.Canvas(buffer, pagesize=(label_width, label_height))

    margin = 3 * mm
    logo_size = 10 * mm
    logo_y = label_height - margin - logo_size
    draw_logo(pdf, margin, logo_y, logo_size)

    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(
        margin + logo_size + 2 * mm,
        label_height - margin - 2 * mm,
        "Étiquette entretien",
    )

    pdf.setFont("Helvetica", 8)
    current_y = logo_y - 4 * mm
    pdf.drawString(margin, current_y, f"Code : {care_wig.code}")
    current_y -= 4 * mm
    pdf.drawString(margin, current_y, f"Initiales cliente : {initials}")
    current_y -= 4 * mm
    pdf.drawString(margin, current_y, f"Date promise : {promised}")
    current_y -= 4 * mm
    pdf.drawString(
        margin, current_y, f"Imprimée le : {printed_at.strftime('%d/%m/%Y %H:%M')}"
    )

    qr_data = f"{care_wig.code}|/wigs/care-wigs/{care_wig.pk}/"
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)
    qr_size = 18 * mm
    pdf.drawImage(
        qr_reader,
        label_width - margin - qr_size,
        margin,
        width=qr_size,
        height=qr_size,
    )

    pdf.showPage()
    pdf.save()

    care_wig.label_printed_at = printed_at
    care_wig.save(update_fields=["label_printed_at"])

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f"inline; filename=etiquette-{care_wig.code}.pdf"
    return response


class WigProductViewSet(viewsets.ModelViewSet):
    queryset = WigProduct.objects.all()
    serializer_class = WigProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return apply_filters(queryset, self.request.query_params, ["name", "code"])


class CareWigViewSet(viewsets.ModelViewSet):
    queryset = CareWig.objects.all()
    serializer_class = CareWigSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return apply_filters(queryset, self.request.query_params, ["client", "code"])
