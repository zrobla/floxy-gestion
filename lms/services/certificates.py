from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode

from lms.models import Certificate


def _build_certificate_number(enrollment) -> str:
    date_part = timezone.now().strftime("%Y%m%d")
    return f"FM-{enrollment.course_id}-{enrollment.id}-{date_part}"


def _build_verification_url(certificate) -> str:
    base = getattr(settings, "LMS_CERTIFICATE_VERIFY_BASE_URL", "").strip()
    if not base:
        base = getattr(settings, "SITE_URL", "").strip()
    if not base:
        base = "http://localhost:8000"
    base = base.rstrip("/")
    return f"{base}/api/lms/certificates/verify/{certificate.id}/"


def _render_pdf(enrollment, certificate) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 3 * cm, "Certificat de réussite")

    if getattr(settings, "FLOXY_LOGO_PATH", None):
        try:
            c.drawImage(settings.FLOXY_LOGO_PATH, 2 * cm, height - 4 * cm, width=3 * cm, preserveAspectRatio=True)
        except Exception:
            pass

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 5 * cm, "Cette attestation certifie que")

    full_name = enrollment.user.get_full_name() or enrollment.user.username
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 6.5 * cm, full_name)

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 8 * cm, "a complété le cours")

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 9.5 * cm, enrollment.course.title)

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, 2 * cm, f"Date: {timezone.now().strftime('%d/%m/%Y')}")
    c.drawString(2 * cm, 1.3 * cm, f"Certificat: {certificate.certificate_number}")

    verify_url = _build_verification_url(certificate)
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)
    c.drawImage(qr_reader, width - 5 * cm, 1.5 * cm, width=3 * cm, height=3 * cm)

    c.showPage()
    c.save()
    return buffer.getvalue()


def issue_certificate(enrollment, created_by=None) -> Certificate:
    if enrollment.status != enrollment.Status.COMPLETED:
        raise ValidationError("L'inscription doit être terminée pour émettre un certificat.")

    certificate_number = _build_certificate_number(enrollment)
    certificate, _ = Certificate.objects.get_or_create(
        enrollment=enrollment,
        defaults={
            "certificate_number": certificate_number,
            "issued_at": timezone.now(),
            "created_by": created_by,
        },
    )

    if not certificate.pdf_file:
        pdf_bytes = _render_pdf(enrollment, certificate)
        filename = f"certificate-{certificate.certificate_number}.pdf"
        certificate.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)

    return certificate
