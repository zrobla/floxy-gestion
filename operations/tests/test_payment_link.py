from rest_framework.test import APITestCase

from accounts.models import User
from integrations.models import LoyverseReceipt
from operations.models import Activity, PaymentLink


class PaymentLinkTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager",
            password="Test12345!",
            role=User.Role.MANAGER,
        )

    def test_link_payment_sets_paid_and_amount(self):
        activity = Activity.objects.create(
            type=Activity.Type.SERVICE,
            status=Activity.Status.TO_COLLECT,
            expected_amount=120,
        )
        receipt = LoyverseReceipt.objects.create(raw_json={"id": "abc"})

        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            f"/api/activities/{activity.id}/link_payment/",
            {
                "receipt_id": receipt.id,
                "final_amount": "150.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        activity.refresh_from_db()
        self.assertEqual(activity.status, Activity.Status.PAID)
        self.assertEqual(str(activity.final_amount), "150.00")

        link = PaymentLink.objects.get(activity=activity)
        self.assertEqual(link.loyverse_receipt_id, receipt.id)
