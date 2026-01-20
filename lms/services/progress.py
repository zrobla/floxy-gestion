from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from lms.models import (
    Assignment,
    AssignmentSubmission,
    Lesson,
    Module,
    Progress,
    Quiz,
    Submission,
)


def _required_quizzes(lesson: Lesson):
    return Quiz.objects.filter(lesson=lesson, is_required_for_completion=True)


def _lesson_quiz_passed(enrollment, lesson: Lesson) -> bool:
    required_quizzes = list(_required_quizzes(lesson))
    if not required_quizzes:
        return True
    for quiz in required_quizzes:
        if not Submission.objects.filter(
            enrollment=enrollment, quiz=quiz, passed=True
        ).exists():
            return False
    return True


def mark_lesson_viewed(enrollment, lesson: Lesson) -> Progress:
    progress, _ = Progress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    if not progress.viewed_at:
        progress.viewed_at = timezone.now()
    progress.quiz_passed = _lesson_quiz_passed(enrollment, lesson)

    if progress.viewed_at and progress.quiz_passed:
        progress.completed = True
        progress.completed_at = progress.completed_at or timezone.now()
    progress.save(
        update_fields=["viewed_at", "quiz_passed", "completed", "completed_at", "updated_at"]
    )
    return progress


def update_progress_for_quiz(submission: Submission) -> Progress | None:
    lesson = submission.quiz.lesson
    if not lesson:
        return None
    progress, _ = Progress.objects.get_or_create(
        enrollment=submission.enrollment, lesson=lesson
    )
    progress.quiz_passed = _lesson_quiz_passed(submission.enrollment, lesson)
    if progress.viewed_at and progress.quiz_passed:
        progress.completed = True
        progress.completed_at = progress.completed_at or timezone.now()
    progress.save(
        update_fields=["quiz_passed", "completed", "completed_at", "updated_at"]
    )
    return progress


def is_module_completed(enrollment, module: Module) -> bool:
    lessons = Lesson.objects.filter(module=module)
    total_lessons = lessons.count()
    completed_lessons = Progress.objects.filter(
        enrollment=enrollment, lesson__module=module, completed=True
    ).count()

    if total_lessons == 0 or completed_lessons < total_lessons:
        return False

    assignments = Assignment.objects.filter(Q(module=module) | Q(lesson__module=module))
    if not assignments.exists():
        return False

    approved_submission_exists = AssignmentSubmission.objects.filter(
        enrollment=enrollment,
        assignment__in=assignments,
        status=AssignmentSubmission.Status.APPROVED,
    ).exists()
    return approved_submission_exists


def is_course_completed(enrollment) -> bool:
    modules = Module.objects.filter(course=enrollment.course)
    if not modules.exists():
        return False

    for module in modules:
        if not is_module_completed(enrollment, module):
            return False

    final_assignments = Assignment.objects.filter(
        Q(module__course=enrollment.course) | Q(lesson__module__course=enrollment.course),
        is_final_assessment=True,
    )
    if not final_assignments.exists():
        return False

    final_approved = AssignmentSubmission.objects.filter(
        enrollment=enrollment,
        assignment__in=final_assignments,
        status=AssignmentSubmission.Status.APPROVED,
    ).exists()
    return final_approved


def refresh_enrollment_progress(enrollment) -> None:
    total_lessons = Lesson.objects.filter(module__course=enrollment.course).count()
    completed_lessons = Progress.objects.filter(
        enrollment=enrollment, completed=True
    ).count()

    progress_percent = (
        Decimal(completed_lessons) / Decimal(total_lessons) * 100
        if total_lessons
        else Decimal("0.00")
    )

    enrollment.progress_percent = progress_percent.quantize(Decimal("0.01"))
    if completed_lessons > 0 and enrollment.status == enrollment.Status.ENROLLED:
        enrollment.status = enrollment.Status.IN_PROGRESS

    if is_course_completed(enrollment):
        enrollment.status = enrollment.Status.COMPLETED
        enrollment.completed_at = enrollment.completed_at or timezone.now()

    enrollment.save(update_fields=["status", "progress_percent", "completed_at", "updated_at"])
