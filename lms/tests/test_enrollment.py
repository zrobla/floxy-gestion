from django.contrib.auth import get_user_model
from django.test import TestCase

from lms.models import Course
from lms.services.enrollment import enroll_user


class EnrollmentServiceTests(TestCase):
    def test_enroll_user_creates_once(self):
        User = get_user_model()
        user = User.objects.create_user(username="learner", password="pass")
        course = Course.objects.create(title="Formation")

        enrollment1 = enroll_user(user, course)
        enrollment2 = enroll_user(user, course)

        self.assertEqual(enrollment1.id, enrollment2.id)
