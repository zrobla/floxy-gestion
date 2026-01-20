from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User


class Command(BaseCommand):
    help = "Crée les utilisateurs initiaux avec leurs rôles."

    def handle(self, *args, **options):
        users_to_create = [
            {
                "username": "owner",
                "email": "owner@floxy.local",
                "role": User.Role.OWNER,
                "password": "Owner12345!",
            },
            {
                "username": "manager",
                "email": "manager@floxy.local",
                "role": User.Role.MANAGER,
                "password": "Manager12345!",
            },
            {
                "username": "admin",
                "email": "admin@floxy.local",
                "role": User.Role.ADMIN,
                "password": "Admin12345!",
            },
            {
                "username": "staff1",
                "email": "staff1@floxy.local",
                "role": User.Role.STAFF,
                "password": "Staff12345!",
            },
            {
                "username": "staff2",
                "email": "staff2@floxy.local",
                "role": User.Role.STAFF,
                "password": "Staff12345!",
            },
            {
                "username": "cashier",
                "email": "cashier@floxy.local",
                "role": User.Role.CASHIER,
                "password": "Cashier12345!",
            },
        ]

        self.stdout.write("Création des utilisateurs initiaux...")

        with transaction.atomic():
            for entry in users_to_create:
                user, created = User.objects.get_or_create(
                    username=entry["username"],
                    defaults={
                        "email": entry["email"],
                        "role": entry["role"],
                    },
                )

                user.email = entry["email"]
                user.role = entry["role"]
                user.is_staff = True
                user.is_superuser = entry["role"] in {User.Role.OWNER, User.Role.ADMIN}
                user.set_password(entry["password"])
                user.save()

                action = "créé" if created else "mis à jour"
                role_label = entry["role"].label
                self.stdout.write(
                    f"- {role_label} {action} : identifiant={entry['username']} "
                    f"mot de passe={entry['password']}"
                )

        self.stdout.write(self.style.SUCCESS("Utilisateurs initiaux prêts."))
