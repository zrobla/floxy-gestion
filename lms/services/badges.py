from decimal import Decimal

from django.db import transaction
from django.db.models import Q, Sum

from lms.models import (
    Assignment,
    AssignmentKPIEvidence,
    AssignmentSubmission,
    Badge,
    BadgeAward,
    Quiz,
    QuizAttempt,
)
from lms.services.progress import is_module_completed


def _best_quiz_percent_for_scope(enrollment, quizzes) -> Decimal:
    best_percent = Decimal("0.00")
    for quiz in quizzes:
        attempts = QuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz)
        for attempt in attempts:
            if attempt.max_score:
                percent = (attempt.score / attempt.max_score) * 100
                if percent > best_percent:
                    best_percent = percent
    return best_percent


def _kpi_total_for_label(enrollment, label: str) -> Decimal:
    if not label:
        return Decimal("0.00")
    total = (
        AssignmentKPIEvidence.objects.filter(
            submission__enrollment=enrollment,
            requirement__label__iexact=label,
        )
        .aggregate(total=Sum("value"))
        .get("total")
    )
    return Decimal(total or 0)


@transaction.atomic
def award_badges_for_enrollment(enrollment) -> list[BadgeAward]:
    awards = []
    for badge in Badge.objects.filter(is_active=True):
        should_award = False

        if badge.rule_type == Badge.RuleType.COURSE_COMPLETED:
            if enrollment.status == enrollment.Status.COMPLETED and (
                not badge.course or badge.course_id == enrollment.course_id
            ):
                should_award = True

        elif badge.rule_type == Badge.RuleType.MODULE_COMPLETED:
            module = badge.module
            if module and module.course_id == enrollment.course_id:
                should_award = is_module_completed(enrollment, module)

        elif badge.rule_type == Badge.RuleType.QUIZ_SCORE:
            if badge.module:
                quizzes = Quiz.objects.filter(
                    Q(module=badge.module) | Q(lesson__module=badge.module)
                )
            else:
                course_id = badge.course_id or enrollment.course_id
                quizzes = Quiz.objects.filter(
                    Q(module__course_id=course_id)
                    | Q(lesson__module__course_id=course_id)
                )
            best_percent = _best_quiz_percent_for_scope(enrollment, quizzes)
            if best_percent >= badge.min_score:
                should_award = True

        elif badge.rule_type == Badge.RuleType.KPI_TARGET:
            total = _kpi_total_for_label(enrollment, badge.kpi_label)
            if badge.kpi_min_value is not None and total >= badge.kpi_min_value:
                should_award = True
        elif badge.rule_type == Badge.RuleType.ASSIGNMENT_APPROVED:
            if badge.assignment:
                should_award = AssignmentSubmission.objects.filter(
                    enrollment=enrollment,
                    assignment=badge.assignment,
                    status=AssignmentSubmission.Status.APPROVED,
                ).exists()
            else:
                assignments = Assignment.objects.none()
                if badge.module:
                    assignments = Assignment.objects.filter(
                        Q(module=badge.module) | Q(lesson__module=badge.module)
                    )
                elif badge.course:
                    assignments = Assignment.objects.filter(
                        Q(module__course=badge.course)
                        | Q(lesson__module__course=badge.course)
                    )
                if assignments.exists():
                    should_award = AssignmentSubmission.objects.filter(
                        enrollment=enrollment,
                        assignment__in=assignments,
                        status=AssignmentSubmission.Status.APPROVED,
                    ).exists()

        if should_award:
            award, _ = BadgeAward.objects.get_or_create(
                badge=badge, user=enrollment.user, defaults={"enrollment": enrollment}
            )
            awards.append(award)

    return awards
