from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from lms.models import (
    AssignmentKPIEvidence,
    AssignmentSubmission,
    AssignmentSubmissionAttachment,
    AssignmentSubmissionKPI,
    AssignmentSubmissionLink,
)
from lms.services.progress import refresh_enrollment_progress


def _validate_kpi_value(requirement, value: Decimal) -> None:
    if requirement.min_value is not None and value < requirement.min_value:
        raise ValidationError(
            {"value": f"{requirement.label}: valeur inférieure au minimum."}
        )
    if requirement.max_value is not None and value > requirement.max_value:
        raise ValidationError(
            {"value": f"{requirement.label}: valeur supérieure au maximum."}
        )


def validate_kpi_evidence(submission: AssignmentSubmission) -> None:
    assignment = submission.assignment
    if not assignment.requires_kpi_evidence:
        return

    evidence_qs = AssignmentKPIEvidence.objects.filter(submission=submission)
    if not evidence_qs.exists():
        raise ValidationError({"kpi": "Aucune preuve KPI fournie."})

    required_requirements = assignment.kpi_requirements.filter(is_required=True)
    evidence_by_req = {e.requirement_id: e for e in evidence_qs}

    for requirement in required_requirements:
        evidence = evidence_by_req.get(requirement.id)
        if not evidence:
            raise ValidationError(
                {"kpi": f"Preuve KPI manquante pour {requirement.label}."}
            )
        if not evidence.proof_url and not evidence.proof_file:
            raise ValidationError(
                {"kpi": f"Preuve (lien ou fichier) requise pour {requirement.label}."}
            )
        _validate_kpi_value(requirement, evidence.value)


@transaction.atomic
def submit_assignment(
    enrollment,
    assignment,
    response_text: str = "",
    evidence_payloads: list[dict] | None = None,
    attachments: list | None = None,
    proof_links: list[str] | None = None,
    kpis: list[dict] | None = None,
) -> AssignmentSubmission:
    submission, _ = AssignmentSubmission.objects.update_or_create(
        enrollment=enrollment,
        assignment=assignment,
        defaults={
            "response_text": response_text,
            "status": AssignmentSubmission.Status.SUBMITTED,
            "feedback": "",
            "reviewed_at": None,
            "reviewed_by": None,
        },
    )

    if evidence_payloads is not None:
        AssignmentKPIEvidence.objects.filter(submission=submission).delete()
        for payload in evidence_payloads:
            AssignmentKPIEvidence.objects.create(
                submission=submission,
                requirement=payload.get("requirement"),
                value=payload.get("value"),
                proof_url=payload.get("proof_url", ""),
                proof_file=payload.get("proof_file"),
                notes=payload.get("notes", ""),
                crm_client=payload.get("crm_client"),
                activity=payload.get("activity"),
            )

    if attachments is not None:
        AssignmentSubmissionAttachment.objects.filter(submission=submission).delete()
        for attachment in attachments:
            if not attachment:
                continue
            AssignmentSubmissionAttachment.objects.create(
                submission=submission,
                image=attachment,
            )

    if proof_links is not None:
        AssignmentSubmissionLink.objects.filter(submission=submission).delete()
        for link in proof_links:
            if not link:
                continue
            AssignmentSubmissionLink.objects.create(submission=submission, url=link)

    if kpis is not None:
        AssignmentSubmissionKPI.objects.filter(submission=submission).delete()
        for kpi in kpis:
            AssignmentSubmissionKPI.objects.create(
                submission=submission,
                label=kpi.get("label", ""),
                value=kpi.get("value"),
                unit=kpi.get("unit", ""),
            )

    validate_kpi_evidence(submission)
    return submission


@transaction.atomic
def review_submission(
    submission: AssignmentSubmission,
    reviewer,
    status: str,
    feedback: str = "",
) -> AssignmentSubmission:
    if not reviewer or getattr(reviewer, "role", None) not in {"OWNER", "ADMIN", "MANAGER"}:
        raise ValidationError("Accès réservé aux superviseurs.")
    if status not in {
        AssignmentSubmission.Status.APPROVED,
        AssignmentSubmission.Status.REJECTED,
    }:
        raise ValidationError("Statut de validation invalide.")
    submission.status = status
    submission.feedback = feedback
    submission.reviewed_at = timezone.now()
    submission.reviewed_by = reviewer
    submission.save(update_fields=["status", "feedback", "reviewed_at", "reviewed_by", "updated_at"])
    refresh_enrollment_progress(submission.enrollment)
    return submission
