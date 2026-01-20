from django.utils import timezone
from rest_framework.test import APITestCase

from wigs.models import CareWig


class CareWigLabelTests(APITestCase):
    def test_label_pdf_returns_pdf_and_updates_timestamp(self):
        care_wig = CareWig.objects.create(client="Cliente Test")

        response = self.client.get(f"/wigs/care-wigs/{care_wig.pk}/label.pdf")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

        care_wig.refresh_from_db()
        self.assertIsNotNone(care_wig.label_printed_at)
        self.assertLessEqual(care_wig.label_printed_at, timezone.now())
