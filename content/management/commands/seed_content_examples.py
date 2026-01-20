from django.core.management.base import BaseCommand

from content.models import ContentItem


class Command(BaseCommand):
    help = "Crée des exemples de contenu pour le planner social media."

    def handle(self, *args, **options):
        examples = [
            {
                "title": "Teaser nouvelle collection",
                "description": "Visuel avant la sortie de la nouvelle collection.",
                "status": ContentItem.Status.IDEA,
            },
            {
                "title": "Tutoriel coiffure rapide",
                "description": "Mini vidéo pour expliquer une pose rapide.",
                "status": ContentItem.Status.IN_CREATION,
            },
            {
                "title": "Story coulisses",
                "description": "Story sur la préparation en atelier.",
                "status": ContentItem.Status.BRIEF,
            },
        ]

        created_count = 0
        for example in examples:
            item, created = ContentItem.objects.get_or_create(
                title=example["title"],
                defaults={
                    "description": example["description"],
                    "status": example["status"],
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Exemples de contenu créés : {created_count}")
        )
