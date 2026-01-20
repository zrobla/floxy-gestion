from django.contrib.auth import get_user_model
from django.test import TestCase

from training.models import (
    TrainingChecklistProgress,
    TrainingEnrollment,
    TrainingLesson,
    TrainingLessonChecklistItem,
    TrainingProgram,
    TrainingProgress,
    TrainingWeek,
)
from training.utils import lesson_completion_status


class LessonCompletionRulesTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="pass",
            role="MANAGER",
        )
        self.program = TrainingProgram.objects.create(title="Programme test", slug="prog-test")
        self.week = TrainingWeek.objects.create(
            program=self.program, week_number=1, title="S1", objective="Obj"
        )
        self.lesson = TrainingLesson.objects.create(
            week=self.week, title="Module 1", order=1
        )

    def _enroll(self):
        return TrainingEnrollment.objects.create(user=self.user, program=self.program)

    def _required_items(self):
        return [
            TrainingLessonChecklistItem.objects.create(
                lesson=self.lesson, label="Item A", is_required=True, order=1
            ),
            TrainingLessonChecklistItem.objects.create(
                lesson=self.lesson, label="Item B", is_required=True, order=2
            ),
        ]

    def test_manual_completable(self):
        self._enroll()
        self.lesson.completion_mode = TrainingLesson.CompletionMode.MANUAL
        self.lesson.save(update_fields=["completion_mode"])
        status = lesson_completion_status(self.user, self.lesson)
        self.assertTrue(status["is_eligible"])

    def test_checklist_only(self):
        enrollment = self._enroll()
        self.lesson.completion_mode = TrainingLesson.CompletionMode.CHECKLIST_ONLY
        self.lesson.save(update_fields=["completion_mode"])
        items = self._required_items()
        status = lesson_completion_status(self.user, self.lesson)
        self.assertFalse(status["is_eligible"])

        for item in items:
            TrainingChecklistProgress.objects.create(
                enrollment=enrollment, checklist_item=item, is_done=True
            )
        status = lesson_completion_status(self.user, self.lesson)
        self.assertTrue(status["is_eligible"])

    def test_quiz_only(self):
        enrollment = self._enroll()
        self.lesson.completion_mode = TrainingLesson.CompletionMode.QUIZ_ONLY
        self.lesson.save(update_fields=["completion_mode"])
        status = lesson_completion_status(self.user, self.lesson)
        self.assertFalse(status["is_eligible"])

        TrainingProgress.objects.create(
            enrollment=enrollment, lesson=self.lesson, quiz_passed=True
        )
        status = lesson_completion_status(self.user, self.lesson)
        self.assertTrue(status["is_eligible"])

    def test_checklist_and_quiz(self):
        enrollment = self._enroll()
        self.lesson.completion_mode = TrainingLesson.CompletionMode.CHECKLIST_AND_QUIZ
        self.lesson.save(update_fields=["completion_mode"])
        items = self._required_items()
        TrainingProgress.objects.create(
            enrollment=enrollment, lesson=self.lesson, quiz_passed=True
        )
        status = lesson_completion_status(self.user, self.lesson)
        self.assertFalse(status["is_eligible"])

        for item in items:
            TrainingChecklistProgress.objects.create(
                enrollment=enrollment, checklist_item=item, is_done=True
            )
        status = lesson_completion_status(self.user, self.lesson)
        self.assertTrue(status["is_eligible"])

    def test_checklist_quiz_and_submission(self):
        enrollment = self._enroll()
        self.lesson.completion_mode = (
            TrainingLesson.CompletionMode.CHECKLIST_QUIZ_AND_SUBMISSION
        )
        self.lesson.save(update_fields=["completion_mode"])
        items = self._required_items()
        progress = TrainingProgress.objects.create(
            enrollment=enrollment, lesson=self.lesson, quiz_passed=True, submission_done=False
        )
        status = lesson_completion_status(self.user, self.lesson)
        self.assertFalse(status["is_eligible"])

        for item in items:
            TrainingChecklistProgress.objects.create(
                enrollment=enrollment, checklist_item=item, is_done=True
            )
        progress.submission_done = True
        progress.save(update_fields=["submission_done"])
        status = lesson_completion_status(self.user, self.lesson)
        self.assertTrue(status["is_eligible"])
