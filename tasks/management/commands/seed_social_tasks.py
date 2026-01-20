from django.core.management.base import BaseCommand

from tasks.models import RecurrenceRule, TaskTemplate


class Command(BaseCommand):
    help = "Crée les modèles de tâches réseaux sociaux standards."

    def handle(self, *args, **options):
        daily_rule, _ = RecurrenceRule.objects.get_or_create(
            name="Réseaux sociaux quotidien",
            defaults={
                "frequency": RecurrenceRule.Frequency.DAILY,
                "interval": 1,
                "description": "Tâches quotidiennes de communication.",
            },
        )
        weekly_rule, _ = RecurrenceRule.objects.get_or_create(
            name="Réseaux sociaux hebdomadaire",
            defaults={
                "frequency": RecurrenceRule.Frequency.WEEKLY,
                "interval": 1,
                "weekdays": "0",
                "description": "Tâches hebdomadaires de communication.",
            },
        )

        templates = [
            {
                "name": "Stories quotidiennes",
                "description": "Publier une story et répondre aux réactions.",
                "recurrence_rule": daily_rule,
            },
            {
                "name": "Réponses aux DM",
                "description": "Répondre aux messages privés en attente.",
                "recurrence_rule": daily_rule,
            },
            {
                "name": "Avant/Après",
                "description": "Publier un avant/après client du jour.",
                "recurrence_rule": daily_rule,
            },
            {
                "name": "Promo hebdomadaire",
                "description": "Préparer la promotion hebdomadaire.",
                "recurrence_rule": weekly_rule,
            },
        ]

        created_count = 0
        for data in templates:
            template, created = TaskTemplate.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "recurrence_rule": data["recurrence_rule"],
                    "is_active": True,
                },
            )
            if not created:
                template.description = data["description"]
                template.recurrence_rule = data["recurrence_rule"]
                template.is_active = True
                template.save(
                    update_fields=["description", "recurrence_rule", "is_active"]
                )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Modèles réseaux sociaux créés : {created_count}")
        )
