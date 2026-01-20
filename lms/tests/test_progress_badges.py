from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from lms.models import (
    Assignment,
    AssignmentSubmission,
    Badge,
    Course,
    Lesson,
    Module,
    Progress,
)
from lms.models import Enrollment
from lms.services.badges import award_badges_for_enrollment
from lms.services.certificates import issue_certificate
from lms.services.progress import (
    is_module_completed,
    mark_lesson_viewed,
    refresh_enrollment_progress,
)


class ProgressBadgeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="learner", password="pass")
        self.course = Course.objects.create(title="Formation")
        self.module = Module.objects.create(
            course=self.course, week_number=1, title="S1", order=1
        )
        self.lesson = Lesson.objects.create(module=self.module, title="Intro", order=1)
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        self.assignment = Assignment.objects.create(
            lesson=self.lesson, title="Mission", requires_kpi_evidence=False
        )

    def test_module_completion_rule(self):
        mark_lesson_viewed(self.enrollment, self.lesson)
        Progress.objects.filter(enrollment=self.enrollment, lesson=self.lesson).update(
            quiz_passed=True, completed=True, completed_at=timezone.now()
        )
        AssignmentSubmission.objects.create(
            enrollment=self.enrollment,
            assignment=self.assignment,
            status=AssignmentSubmission.Status.APPROVED,
        )
        self.assertTrue(is_module_completed(self.enrollment, self.module))

    def test_course_completion(self):
        mark_lesson_viewed(self.enrollment, self.lesson)
        Progress.objects.filter(enrollment=self.enrollment, lesson=self.lesson).update(
            quiz_passed=True, completed=True, completed_at=timezone.now()
        )
        AssignmentSubmission.objects.create(
            enrollment=self.enrollment,
            assignment=self.assignment,
            status=AssignmentSubmission.Status.APPROVED,
        )
        final_assessment = Assignment.objects.create(
            module=self.module,
            title="Examen final",
            is_final_assessment=True,
        )
        AssignmentSubmission.objects.create(
            enrollment=self.enrollment,
            assignment=final_assessment,
            status=AssignmentSubmission.Status.APPROVED,
        )
        refresh_enrollment_progress(self.enrollment)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, self.enrollment.Status.COMPLETED)

    def test_badge_award_and_certificate(self):
        mark_lesson_viewed(self.enrollment, self.lesson)
        Progress.objects.filter(enrollment=self.enrollment, lesson=self.lesson).update(
            quiz_passed=True, completed=True, completed_at=timezone.now()
        )
        AssignmentSubmission.objects.create(
            enrollment=self.enrollment,
            assignment=self.assignment,
            status=AssignmentSubmission.Status.APPROVED,
        )
        final_assessment = Assignment.objects.create(
            module=self.module,
            title="Examen final",
            is_final_assessment=True,
        )
        AssignmentSubmission.objects.create(
            enrollment=self.enrollment,
            assignment=final_assessment,
            status=AssignmentSubmission.Status.APPROVED,
        )
        refresh_enrollment_progress(self.enrollment)
        badge = Badge.objects.create(
            name="Diplômé", rule_type=Badge.RuleType.COURSE_COMPLETED, course=self.course
        )
        awards = award_badges_for_enrollment(self.enrollment)
        self.assertEqual(len(awards), 1)
        certificate = issue_certificate(self.enrollment)
        self.assertTrue(certificate.pdf_file)

    def test_badge_award_assignment_approved(self):
        badge = Badge.objects.create(
            name="Mission validée",
            rule_type=Badge.RuleType.ASSIGNMENT_APPROVED,
            assignment=self.assignment,
        )
        awards = award_badges_for_enrollment(self.enrollment)
        self.assertEqual(len(awards), 0)

        AssignmentSubmission.objects.create(
            enrollment=self.enrollment,
            assignment=self.assignment,
            status=AssignmentSubmission.Status.APPROVED,
        )
        awards = award_badges_for_enrollment(self.enrollment)
        self.assertEqual(len(awards), 1)
