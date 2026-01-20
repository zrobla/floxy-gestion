from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from operations.models import Activity


class ActivityStatusTests(TestCase):
    def test_status_transitions(self):
        activity = Activity.objects.create(
            type=Activity.Type.SERVICE, expected_amount=0
        )

        activity.set_status(Activity.Status.IN_PROGRESS)
        self.assertEqual(activity.status, Activity.Status.IN_PROGRESS)

        activity.set_status(Activity.Status.DONE)
        self.assertEqual(activity.status, Activity.Status.DONE)

        activity.set_status(Activity.Status.TO_COLLECT)
        self.assertEqual(activity.status, Activity.Status.TO_COLLECT)

        activity.set_status(Activity.Status.PAID)
        self.assertEqual(activity.status, Activity.Status.PAID)

    def test_invalid_transition_raises(self):
        activity = Activity.objects.create(
            type=Activity.Type.SERVICE, expected_amount=0
        )

        with self.assertRaises(ValidationError):
            activity.set_status(Activity.Status.PAID)

    def test_can_cancel_from_in_progress(self):
        activity = Activity.objects.create(
            type=Activity.Type.SERVICE, expected_amount=0
        )

        activity.set_status(Activity.Status.IN_PROGRESS)
        activity.set_status(Activity.Status.CANCELED)

        self.assertEqual(activity.status, Activity.Status.CANCELED)


class ActivityValidationTests(TestCase):
    def test_estimated_end_at_after_start_at(self):
        activity = Activity.objects.create(
            type=Activity.Type.SERVICE, expected_amount=0
        )
        activity.start_at = timezone.now()
        activity.estimated_end_at = activity.start_at - timedelta(hours=2)

        with self.assertRaises(ValidationError):
            activity.full_clean()

    def test_end_at_after_start_at(self):
        activity = Activity.objects.create(
            type=Activity.Type.SERVICE, expected_amount=0
        )
        activity.start_at = timezone.now()
        activity.end_at = activity.start_at - timedelta(hours=1)

        with self.assertRaises(ValidationError):
            activity.full_clean()
