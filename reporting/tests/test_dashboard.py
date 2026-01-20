from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import User
from content.models import ContentApproval, ContentItem, ContentMetric
from tasks.models import Task


class DashboardRendementTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="Test12345!",
            role=User.Role.OWNER,
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="Test12345!",
            role=User.Role.ADMIN,
        )
        self.manager = User.objects.create_user(
            username="manager",
            password="Test12345!",
            role=User.Role.MANAGER,
        )

    def test_dashboard_returns_metrics(self):
        today = timezone.localdate()

        task_late = Task.objects.create(
            title="Tâche en retard",
            status=Task.Status.DONE,
            due_date=today - timedelta(days=1),
        )
        task_ok = Task.objects.create(
            title="Tâche à l'heure",
            status=Task.Status.DONE,
            due_date=today,
        )
        Task.objects.filter(pk=task_late.pk).update(updated_at=timezone.now())
        Task.objects.filter(pk=task_ok.pk).update(updated_at=timezone.now())

        item_instagram = ContentItem.objects.create(
            title="Post IG",
            status=ContentItem.Status.PUBLISHED,
            platform=ContentItem.Platform.INSTAGRAM,
        )
        item_tiktok = ContentItem.objects.create(
            title="Post TikTok",
            status=ContentItem.Status.METRICS_RECORDED,
            platform=ContentItem.Platform.TIKTOK,
        )
        ContentItem.objects.create(
            title="Post IG 2",
            status=ContentItem.Status.IDEA,
            platform=ContentItem.Platform.INSTAGRAM,
        )

        ContentApproval.objects.create(
            content_item=item_instagram,
            approved_by=self.owner,
            comment="Validé",
            approved=True,
        )
        ContentApproval.objects.create(
            content_item=item_tiktok,
            approved_by=self.owner,
            comment="Refusé",
            approved=False,
        )

        ContentMetric.objects.create(
            content_item=item_instagram,
            likes=100,
            comments=10,
            shares=5,
            saves=5,
            reach=1000,
            clicks=20,
        )
        ContentMetric.objects.create(
            content_item=item_tiktok,
            likes=50,
            comments=5,
            shares=5,
            saves=0,
            reach=600,
            clicks=10,
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/reporting/dashboard/rendement")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["taches"]["terminees"], 2)
        self.assertEqual(response.data["taches"]["en_retard"], 1)
        self.assertEqual(response.data["contenus_par_plateforme"].get("Instagram"), 2)
        self.assertEqual(response.data["contenus_par_plateforme"].get("TikTok"), 1)
        self.assertEqual(response.data["taux_validation"]["approuves"], 1)
        self.assertEqual(response.data["taux_validation"]["soumis"], 2)
        self.assertEqual(response.data["taux_validation"]["taux"], 50.0)
        self.assertEqual(response.data["score_moyen_contenu"], 11.0)

    def test_manager_cannot_access_dashboard(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.get("/reporting/dashboard/rendement")

        self.assertEqual(response.status_code, 403)
