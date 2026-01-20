from __future__ import annotations

from training.models import (
    TrainingChecklistProgress,
    TrainingEnrollment,
    TrainingLesson,
    TrainingLessonChecklistItem,
    TrainingProgress,
)


def lesson_completion_status(user, lesson: TrainingLesson) -> dict:
    mode = lesson.completion_mode
    status = {
        "mode": mode,
        "mode_label": lesson.get_completion_mode_display(),
        "is_eligible": True,
        "missing": [],
        "missing_display": "",
    }

    if mode == TrainingLesson.CompletionMode.MANUAL:
        return status

    enrollment = TrainingEnrollment.objects.filter(
        program=lesson.week.program, user=user
    ).first()
    if not enrollment:
        status["is_eligible"] = False
        status["missing"] = ["inscription à la formation"]
        status["missing_display"] = "inscription à la formation"
        return status

    progress = TrainingProgress.objects.filter(
        enrollment=enrollment, lesson=lesson
    ).first()

    requires_checklist = mode in {
        TrainingLesson.CompletionMode.CHECKLIST_ONLY,
        TrainingLesson.CompletionMode.CHECKLIST_AND_QUIZ,
        TrainingLesson.CompletionMode.CHECKLIST_QUIZ_AND_SUBMISSION,
    }
    requires_quiz = mode in {
        TrainingLesson.CompletionMode.QUIZ_ONLY,
        TrainingLesson.CompletionMode.CHECKLIST_AND_QUIZ,
        TrainingLesson.CompletionMode.CHECKLIST_QUIZ_AND_SUBMISSION,
    }
    requires_submission = mode == TrainingLesson.CompletionMode.CHECKLIST_QUIZ_AND_SUBMISSION

    missing = []

    if requires_checklist:
        required_items = TrainingLessonChecklistItem.objects.filter(
            lesson=lesson, is_required=True
        )
        if required_items.exists():
            done_ids = set(
                TrainingChecklistProgress.objects.filter(
                    enrollment=enrollment, checklist_item__in=required_items, is_done=True
                ).values_list("checklist_item_id", flat=True)
            )
            missing_count = required_items.exclude(id__in=done_ids).count()
            if missing_count:
                missing.append(f"{missing_count} élément(s) de checklist obligatoire")

    if requires_quiz:
        if not (progress and progress.quiz_passed):
            missing.append("quiz")

    if requires_submission:
        if not (progress and progress.submission_done):
            missing.append("soumission")

    status["missing"] = missing
    status["missing_display"] = ", ".join(missing)
    status["is_eligible"] = len(missing) == 0
    return status


def lesson_is_completable(user, lesson: TrainingLesson) -> bool:
    return lesson_completion_status(user, lesson)["is_eligible"]
