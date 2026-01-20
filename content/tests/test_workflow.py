from rest_framework.test import APITestCase

from accounts.models import User
from content.models import ContentItem


class ContentWorkflowTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="Test12345!",
            role=User.Role.OWNER,
        )
        self.manager = User.objects.create_user(
            username="manager",
            password="Test12345!",
            role=User.Role.MANAGER,
        )

    def test_submit_and_approve(self):
        content_item = ContentItem.objects.create(
            title="Post test", status=ContentItem.Status.IN_CREATION
        )

        self.client.force_authenticate(user=self.manager)
        submit_response = self.client.post(
            f"/api/content/items/{content_item.id}/submit_for_approval/"
        )
        self.assertEqual(submit_response.status_code, 200)

        self.client.force_authenticate(user=self.owner)
        approve_response = self.client.post(
            f"/api/content/items/{content_item.id}/approve/",
            {"comment": "Validé"},
            format="json",
        )
        self.assertEqual(approve_response.status_code, 200)
        content_item.refresh_from_db()
        self.assertEqual(content_item.status, ContentItem.Status.APPROVED)

    def test_reject_returns_to_creation(self):
        content_item = ContentItem.objects.create(
            title="Post test", status=ContentItem.Status.TO_VALIDATE
        )

        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            f"/api/content/items/{content_item.id}/reject/",
            {"comment": "À revoir"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        content_item.refresh_from_db()
        self.assertEqual(content_item.status, ContentItem.Status.IN_CREATION)

    def test_manager_cannot_approve(self):
        content_item = ContentItem.objects.create(
            title="Post test", status=ContentItem.Status.TO_VALIDATE
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            f"/api/content/items/{content_item.id}/approve/",
            {"comment": "Validé"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
