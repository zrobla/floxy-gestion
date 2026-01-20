from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from tasks.models import Task, TaskChecklistItem, TaskTemplate


class Command(BaseCommand):
    help = "Génère les tâches récurrentes pour la date du jour."

    def handle(self, *args, **options):
        today = timezone.localdate()
        templates = TaskTemplate.objects.select_related("recurrence_rule").filter(
            is_active=True, recurrence_rule__isnull=False
        )

        created_count = 0
        skipped_count = 0

        for template in templates:
            rule = template.recurrence_rule
            if not rule or not rule.should_run_on(today):
                continue

            exists = Task.objects.filter(
                template=template, created_at__date=today
            ).exists()
            if exists:
                skipped_count += 1
                continue

            with transaction.atomic():
                task = Task.objects.create(
                    title=template.name,
                    description=template.description,
                    template=template,
                )
                checklist_items = list(template.checklist_items.all())
                if checklist_items:
                    TaskChecklistItem.objects.bulk_create(
                        [
                            TaskChecklistItem(
                                task=task,
                                label=item.label,
                                order=item.order,
                            )
                            for item in checklist_items
                        ]
                    )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Tâches créées : {created_count} | Tâches ignorées : {skipped_count}"
            )
        )
