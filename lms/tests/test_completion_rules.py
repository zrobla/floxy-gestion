from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from lms.models import Assignment, AssignmentSubmission, Choice, Course, Lesson, Module, Quiz, Question
from lms.models import Enrollment, Progress
from lms.services.progress import is_course_completed, is_module_completed, mark_lesson_viewed, refresh_enrollment_progress
from lms.services.quiz import score_quiz_attempt


class CompletionRuleTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="learner", password="pass")
        self.course = Course.objects.create(title="Formation")
        self.module = Module.objects.create(
            course=self.course, week_number=1, title="S1", order=1
        )
        self.lesson = Lesson.objects.create(module=self.module, title="Intro", order=1)
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)

        self.quiz = Quiz.objects.create(
            lesson=self.lesson,
            title="Quiz intro",
            passing_score=70,
            is_required_for_completion=True,
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_type=Question.QuestionType.MCQ,
            prompt="Q1",
            points=1,
            order=1,
        )
        self.choice_ok = Choice.objects.create(
            question=self.question, text="A", is_correct=True
        )

        self.assignment = Assignment.objects.create(
            lesson=self.lesson,
            title="Mission",
            requires_kpi_evidence=False,
        )
        self.final_assignment = Assignment.objects.create(
            module=self.module,
            title="Examen final",
            is_final_assessment=True,
        )

    def test_lesson_completed_requires_view_and_quiz(self):
        progress = mark_lesson_viewed(self.enrollment, self.lesson)
        self.assertFalse(progress.completed)

        score_quiz_attempt(
            self.enrollment,
            self.quiz,
            [{"question_id": self.question.id, "choice_id": self.choice_ok.id}],
        )
        progress.refresh_from_db()
        self.assertTrue(progress.quiz_passed)
        self.assertTrue(progress.completed)

    def test_module_requires_assignment_approved(self):
        mark_lesson_viewed(self.enrollment, self.lesson)
        Progress.objects.filter(enrollment=self.enrollment, lesson=self.lesson).update(
            quiz_passed=True, completed=True, completed_at=timezone.now()
        )
        self.assertFalse(is_module_completed(self.enrollment, self.module))
        AssignmentSubmission.objects.create(
            enrollment=self.enrollment,
            assignment=self.assignment,
            status=AssignmentSubmission.Status.APPROVED,
        )
        self.assertTrue(is_module_completed(self.enrollment, self.module))

    def test_course_requires_final_assessment(self):
        mark_lesson_viewed(self.enrollment, self.lesson)
        Progress.objects.filter(enrollment=self.enrollment, lesson=self.lesson).update(
            quiz_passed=True, completed=True, completed_at=timezone.now()
        )
        AssignmentSubmission.objects.create(
            enrollment=self.enrollment,
            assignment=self.assignment,
            status=AssignmentSubmission.Status.APPROVED,
        )
        self.assertFalse(is_course_completed(self.enrollment))
        AssignmentSubmission.objects.create(
            enrollment=self.enrollment,
            assignment=self.final_assignment,
            status=AssignmentSubmission.Status.APPROVED,
        )
        self.assertTrue(is_course_completed(self.enrollment))
        refresh_enrollment_progress(self.enrollment)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, self.enrollment.Status.COMPLETED)
