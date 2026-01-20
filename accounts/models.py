from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Propriétaire"
        MANAGER = "MANAGER", "Gestionnaire"
        ADMIN = "ADMIN", "Administrateur"
        STAFF = "STAFF", "Employé"
        CASHIER = "CASHIER", "Caissier"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF,
        verbose_name="Rôle",
        help_text="Définit le niveau d'accès de l'utilisateur.",
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
