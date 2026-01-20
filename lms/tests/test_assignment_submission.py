from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from lms.models import Assignment, AssignmentKPIRequirement, Course, Lesson, Module
from lms.models import Enrollment
from lms.services.assignments import submit_assignment


class AssignmentSubmissionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="learner", password="pass")
        self.course = Course.objects.create(title="Formation")
        self.module = Module.objects.create(
            course=self.course, week_number=1, title="S1", order=1
        )
        self.lesson = Lesson.objects.create(module=self.module, title="Intro", order=1)
        self.assignment = Assignment.objects.create(
            lesson=self.lesson, title="Mission KPI", requires_kpi_evidence=True
        )
        self.requirement = AssignmentKPIRequirement.objects.create(
            assignment=self.assignment,
            label="Leads créés",
            unit="leads",
            min_value=Decimal("5"),
        )
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)

    def test_missing_kpi_evidence_raises(self):
        with self.assertRaises(ValidationError):
            submit_assignment(self.enrollment, self.assignment, response_text="OK")

    def test_invalid_kpi_value_raises(self):
        with self.assertRaises(ValidationError):
            submit_assignment(
                self.enrollment,
                self.assignment,
                evidence_payloads=[
                    {
                        "requirement": self.requirement,
                        "value": Decimal("2"),
                        "proof_url": "https://example.com/proof",
                    }
                ],
            )

    def test_valid_kpi_submission(self):
        submission = submit_assignment(
            self.enrollment,
            self.assignment,
            response_text="Fait",
            evidence_payloads=[
                {
                    "requirement": self.requirement,
                    "value": Decimal("8"),
                    "proof_url": "https://example.com/proof",
                }
            ],
        )
        self.assertEqual(submission.assignment, self.assignment)
        self.assertEqual(submission.kpi_evidence.count(), 1)
