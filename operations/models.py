from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ServiceCategory(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Catégorie")
    description = models.TextField(blank=True, verbose_name="Description")
    image_path = models.CharField(
        max_length=255, blank=True, verbose_name="Visuel (statique)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Catégorie de prestation"
        verbose_name_plural = "Catégories de prestation"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    category = models.ForeignKey(
        ServiceCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="services",
        verbose_name="Catégorie",
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Prix de base",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Activity(models.Model):
    class Type(models.TextChoices):
        SERVICE = "SERVICE", "Prestation"
        PRODUCT_PURCHASE = "PRODUCT_PURCHASE", "Achat produit"

    class Status(models.TextChoices):
        ARRIVED = "ARRIVED", "Arrivée"
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        DONE = "DONE", "Terminée"
        TO_COLLECT = "TO_COLLECT", "À encaisser"
        PAID = "PAID", "Payée"
        CANCELED = "CANCELED", "Annulée"

    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        verbose_name="Type d'activité",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ARRIVED,
        verbose_name="Statut",
    )
    client = models.CharField(max_length=255, blank=True, verbose_name="Client")
    assigned_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
        verbose_name="Collaborateur assigné",
    )
    start_at = models.DateTimeField(auto_now_add=True, verbose_name="Début")
    estimated_end_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Fin estimée"
    )
    end_at = models.DateTimeField(null=True, blank=True, verbose_name="Fin réelle")
    expected_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Montant attendu",
    )
    final_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Montant final",
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    content_possible = models.BooleanField(
        default=False, verbose_name="Contenu possible"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Activité"
        verbose_name_plural = "Activités"

    STATUS_FLOW = {
        Status.ARRIVED: {Status.IN_PROGRESS, Status.CANCELED},
        Status.IN_PROGRESS: {Status.DONE, Status.CANCELED},
        Status.DONE: {Status.TO_COLLECT, Status.CANCELED},
        Status.TO_COLLECT: {Status.PAID, Status.CANCELED},
        Status.PAID: set(),
        Status.CANCELED: set(),
    }

    def __str__(self) -> str:
        return f"{self.get_type_display()} - {self.get_status_display()}"

    def clean(self) -> None:
        super().clean()
        if (
            self.estimated_end_at
            and self.start_at
            and self.estimated_end_at < self.start_at
        ):
            raise ValidationError(
                {"estimated_end_at": "La fin estimée doit être après le début."}
            )
        if self.end_at and self.start_at and self.end_at < self.start_at:
            raise ValidationError({"end_at": "La fin réelle doit être après le début."})

    def set_status(self, new_status: str, save: bool = True) -> None:
        if new_status == self.status:
            return
        allowed = self.STATUS_FLOW.get(self.status, set())
        if new_status not in allowed:
            raise ValidationError("Transition de statut non autorisée.")
        self.status = new_status
        if save:
            self.save(update_fields=["status", "updated_at"])

    def mark_done(self, save: bool = True) -> None:
        self.set_status(self.Status.DONE, save=False)
        self.end_at = self.end_at or timezone.now()
        if save:
            self.save(update_fields=["status", "end_at", "updated_at"])


class ActivityLine(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Activité",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_lines",
        verbose_name="Service",
    )
    description = models.CharField(
        max_length=255, blank=True, verbose_name="Description"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Prix unitaire",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Ligne d'activité"
        verbose_name_plural = "Lignes d'activité"

    def __str__(self) -> str:
        label = self.service.name if self.service else self.description or "Ligne"
        return f"{self.activity_id} - {label}"


class PaymentLink(models.Model):
    activity = models.OneToOneField(
        Activity,
        on_delete=models.CASCADE,
        related_name="payment_link",
        verbose_name="Activité",
    )
    loyverse_receipt = models.ForeignKey(
        "integrations.LoyverseReceipt",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payment_links",
        verbose_name="Reçu Loyverse",
    )
    manual_reference = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Référence manuelle",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Lien de paiement"
        verbose_name_plural = "Liens de paiement"

    def __str__(self) -> str:
        return f"{self.activity}"

    def clean(self) -> None:
        super().clean()
        if not self.loyverse_receipt and not self.manual_reference:
            raise ValidationError(
                "Une référence manuelle ou un reçu Loyverse est requis."
            )
