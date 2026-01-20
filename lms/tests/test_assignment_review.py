from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from lms.models import Assignment, Course, Enrollment, Lesson, Module
from lms.services.assignments import review_submission, submit_assignment


class AssignmentReviewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.supervisor = User.objects.create_user(
            username="manager", password="pass", role="MANAGER"
        )
        self.staff = User.objects.create_user(
            username="staff", password="pass", role="STAFF"
        )
        self.course = Course.objects.create(title="Formation")
        self.module = Module.objects.create(
            course=self.course, week_number=1, title="S1", order=1
        )
        self.lesson = Lesson.objects.create(module=self.module, title="Intro", order=1)
        self.assignment = Assignment.objects.create(
            lesson=self.lesson, title="Mission", requires_kpi_evidence=False
        )
        self.enrollment = Enrollment.objects.create(user=self.staff, course=self.course)
        self.submission = submit_assignment(self.enrollment, self.assignment, response_text="OK")

    def test_supervisor_can_approve(self):
        submission = review_submission(
            self.submission,
            reviewer=self.supervisor,
            status=self.submission.Status.APPROVED,
            feedback="Bien fait",
        )
        self.assertEqual(submission.status, submission.Status.APPROVED)
        self.assertEqual(submission.feedback, "Bien fait")
        self.assertEqual(submission.reviewed_by, self.supervisor)

    def test_non_supervisor_cannot_approve(self):
        with self.assertRaises(ValidationError):
            review_submission(
                self.submission,
                reviewer=self.staff,
                status=self.submission.Status.APPROVED,
                feedback="",
            )

    def test_supervisor_can_reject(self):
        submission = review_submission(
            self.submission,
            reviewer=self.supervisor,
            status=self.submission.Status.REJECTED,
            feedback="À refaire",
        )
        self.assertEqual(submission.status, submission.Status.REJECTED)
        self.assertEqual(submission.feedback, "À refaire")
