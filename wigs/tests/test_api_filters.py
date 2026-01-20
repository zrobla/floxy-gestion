from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from wigs.models import CareWig, WigProduct


class WigProductFilterTests(APITestCase):
    def test_filter_by_status(self):
        WigProduct.objects.create(name="Perruque A", status=WigProduct.Status.IN_STOCK)
        WigProduct.objects.create(name="Perruque B", status=WigProduct.Status.SOLD)

        response = self.client.get(
            "/api/wigs/products/", {"status": WigProduct.Status.SOLD}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], WigProduct.Status.SOLD)


class CareWigFilterTests(APITestCase):
    def test_filter_by_start_date(self):
        yesterday = timezone.now() - timedelta(days=1)
        today = timezone.localdate()

        older = CareWig.objects.create(client="Cliente A")
        CareWig.objects.filter(pk=older.pk).update(created_at=yesterday)
        CareWig.objects.create(client="Cliente B")

        response = self.client.get("/api/wigs/care/", {"start_date": today.isoformat()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["client"], "Cliente B")
