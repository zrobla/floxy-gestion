from django.db import models


class LoyverseStore(models.Model):
    token = models.CharField(max_length=255, verbose_name="Jeton API")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Boutique Loyverse"
        verbose_name_plural = "Boutiques Loyverse"

    def __str__(self) -> str:
        return "Boutique Loyverse"


class LoyverseReceipt(models.Model):
    receipt_id = models.CharField(
        max_length=120,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Identifiant",
    )
    raw_json = models.JSONField(verbose_name="Données brutes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Reçu Loyverse"
        verbose_name_plural = "Reçus Loyverse"

    def __str__(self) -> str:
        return f"Reçu {self.receipt_id}"
