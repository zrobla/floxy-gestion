from rest_framework.test import APITestCase

from accounts.models import User
from tasks.models import Task


class TaskWorkflowTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager",
            password="Test12345!",
            role=User.Role.MANAGER,
        )
        self.staff = User.objects.create_user(
            username="staff",
            password="Test12345!",
            role=User.Role.STAFF,
        )

    def test_create_task_and_add_checklist(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            "/api/tasks/tasks/",
            {"title": "Préparer la livraison", "assigned_to": self.staff.id},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        task_id = response.data["id"]

        checklist_response = self.client.post(
            "/api/tasks/checklists/",
            {"task": task_id, "label": "Préparer l'emballage", "order": 1},
            format="json",
        )

        self.assertEqual(checklist_response.status_code, 201)

    def test_staff_can_update_status(self):
        task = Task.objects.create(title="Nettoyer le poste", assigned_to=self.staff)

        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            f"/api/tasks/tasks/{task.id}/set_status/",
            {"status": Task.Status.DONE},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.DONE)
