from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from lms.models import Course, Module, Lesson, Quiz, Choice, Question
from lms.models import Enrollment
from lms.services.quiz import compute_score, score_quiz_attempt


class QuizScoringTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="learner", password="pass")
        self.course = Course.objects.create(title="Formation vente")
        self.module = Module.objects.create(
            course=self.course, week_number=1, title="S1", order=1
        )
        self.lesson = Lesson.objects.create(module=self.module, title="Intro", order=1)
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        self.quiz = Quiz.objects.create(lesson=self.lesson, title="Quiz 1", passing_score=50)

        self.q1 = Question.objects.create(
            quiz=self.quiz,
            question_type=Question.QuestionType.MCQ,
            prompt="Quel est le prix?",
            points=2,
            order=1,
        )
        self.c1 = Choice.objects.create(question=self.q1, text="1000", is_correct=True)
        self.c2 = Choice.objects.create(question=self.q1, text="2000", is_correct=False)

        self.q2 = Question.objects.create(
            quiz=self.quiz,
            question_type=Question.QuestionType.SHORT,
            prompt="Nom de la ville?",
            points=1,
            order=2,
            correct_text="Abidjan",
        )

        self.q3 = Question.objects.create(
            quiz=self.quiz,
            question_type=Question.QuestionType.TRUE_FALSE,
            prompt="Floxy est à Abidjan?",
            points=1,
            order=3,
        )
        self.tf_true = Choice.objects.create(
            question=self.q3, text="Vrai", is_correct=True
        )
        self.tf_false = Choice.objects.create(
            question=self.q3, text="Faux", is_correct=False
        )

    def test_score_quiz_attempt(self):
        attempt = score_quiz_attempt(
            self.enrollment,
            self.quiz,
            [
                {"question_id": self.q1.id, "choice_id": self.c1.id},
                {"question_id": self.q2.id, "text_answer": "abidjan"},
                {"question_id": self.q3.id, "choice_id": self.tf_true.id},
            ],
        )
        self.assertEqual(attempt.score, 4)
        self.assertTrue(attempt.passed)

    def test_max_attempts_enforced(self):
        self.quiz.max_attempts = 1
        self.quiz.save(update_fields=["max_attempts"])
        score_quiz_attempt(
            self.enrollment,
            self.quiz,
            [{"question_id": self.q1.id, "choice_id": self.c1.id}],
        )
        with self.assertRaises(ValidationError):
            score_quiz_attempt(
                self.enrollment,
                self.quiz,
                [{"question_id": self.q1.id, "choice_id": self.c1.id}],
            )

    def test_compute_score_manual_review(self):
        self.q2.manual_review_required = True
        self.q2.save(update_fields=["manual_review_required"])
        submission = score_quiz_attempt(
            self.enrollment,
            self.quiz,
            [
                {"question_id": self.q1.id, "choice_id": self.c1.id},
                {"question_id": self.q2.id, "text_answer": "Abidjan"},
            ],
        )
        short_answer = submission.answers.get(question=self.q2)
        short_answer.manual_scored = True
        short_answer.is_correct = True
        short_answer.score_awarded = 1
        short_answer.save(update_fields=["manual_scored", "is_correct", "score_awarded"])
        compute_score(submission)
        submission.refresh_from_db()
        self.assertEqual(submission.score, 3)
        self.assertTrue(submission.passed)
