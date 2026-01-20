from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from integrations.models import LoyverseReceipt, LoyverseStore


class LoyverseSyncTests(TestCase):
    def setUp(self):
        LoyverseStore.objects.create(token="test-token")

    @patch("integrations.loyverse_client.fetch_receipts")
    def test_sync_is_idempotent(self, mock_fetch):
        mock_fetch.return_value = [
            {"id": "r1", "total": 100},
            {"id": "r2", "total": 200},
        ]

        call_command("sync_loyverse_receipts")
        self.assertEqual(LoyverseReceipt.objects.count(), 2)

        call_command("sync_loyverse_receipts")
        self.assertEqual(LoyverseReceipt.objects.count(), 2)
