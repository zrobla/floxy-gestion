from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class Sequence(models.Model):
    key = models.CharField(max_length=20, unique=True, verbose_name="Clé")
    value = models.PositiveIntegerField(default=0, verbose_name="Compteur")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Séquence"
        verbose_name_plural = "Séquences"

    def __str__(self) -> str:
        return f"{self.key} ({self.value})"


class WigProduct(models.Model):
    class Status(models.TextChoices):
        IN_STOCK = "IN_STOCK", "En stock"
        RESERVED = "RESERVED", "Réservée"
        SOLD = "SOLD", "Vendue"
        RETOUCH = "RETOUCH", "Retouche"
        RETURNED = "RETURNED", "Retour"

    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    name = models.CharField(max_length=150, verbose_name="Nom")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_STOCK,
        verbose_name="Statut",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Prix",
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Perruque"
        verbose_name_plural = "Perruques"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_wig_code(prefix="WIG")
        super().save(*args, **kwargs)


class CareWig(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Reçue"
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        READY = "READY", "Prête"
        DELIVERED = "DELIVERED", "Remise à la cliente"
        CANCELED = "CANCELED", "Annulée"

    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    client = models.CharField(max_length=150, blank=True, verbose_name="Cliente")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
        verbose_name="Statut",
    )
    promised_date = models.DateField(null=True, blank=True, verbose_name="Date promise")
    notes = models.TextField(blank=True, verbose_name="Notes")
    label_printed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Étiquette imprimée le"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Perruque en entretien"
        verbose_name_plural = "Perruques en entretien"

    def __str__(self) -> str:
        label = self.client or "Cliente"
        return f"{self.code} - {label}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_wig_code(prefix="CARE")
        super().save(*args, **kwargs)


def generate_wig_code(prefix: str) -> str:
    if prefix not in {"WIG", "CARE"}:
        raise ValidationError("Préfixe de code invalide.")
    period = timezone.now().strftime("%y%m")
    sequence_key = f"{prefix}-{period}"
    with transaction.atomic():
        sequence, _ = Sequence.objects.select_for_update().get_or_create(
            key=sequence_key, defaults={"value": 0}
        )
        sequence.value += 1
        sequence.save(update_fields=["value", "updated_at"])
        return f"{prefix}-{period}-{sequence.value:04d}"
