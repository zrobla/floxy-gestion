from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Case, IntegerField, Sum, Value, When


class InventoryItem(models.Model):
    class Category(models.TextChoices):
        SALE = "SALE", "Vente"
        CONSUMABLE = "CONSUMABLE", "Consommable"

    name = models.CharField(max_length=150, verbose_name="Nom")
    sku = models.CharField(max_length=60, blank=True, null=True, verbose_name="SKU")
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        verbose_name="Catégorie",
    )
    min_stock = models.PositiveIntegerField(default=0, verbose_name="Stock minimum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self) -> str:
        return self.name

    def get_stock_from_moves(self, exclude_move_id=None) -> int:
        moves = self.moves.all()
        if exclude_move_id:
            moves = moves.exclude(pk=exclude_move_id)
        totals = moves.aggregate(
            total=Sum(
                Case(
                    When(type=StockMove.Type.IN, then=models.F("qty")),
                    When(type=StockMove.Type.ADJUST, then=models.F("qty")),
                    When(type=StockMove.Type.OUT, then=-1 * models.F("qty")),
                    When(type=StockMove.Type.LOSS, then=-1 * models.F("qty")),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
        )
        return totals["total"] or 0

    def get_current_stock(self) -> int:
        return self.get_stock_from_moves()

    def refresh_stock_level(self) -> "StockLevel":
        quantity = self.get_stock_from_moves()
        alert = quantity < self.min_stock
        stock_level, _ = StockLevel.objects.update_or_create(
            item=self,
            defaults={"quantity": quantity, "alert": alert},
        )
        return stock_level


class StockMove(models.Model):
    class Type(models.TextChoices):
        IN = "IN", "Entrée"
        OUT = "OUT", "Sortie"
        ADJUST = "ADJUST", "Ajustement"
        LOSS = "LOSS", "Perte"

    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="moves",
        verbose_name="Article",
    )
    qty = models.IntegerField(verbose_name="Quantité")
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        verbose_name="Type",
    )
    reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Référence",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="stock_moves",
        verbose_name="Créé par",
    )

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"

    def __str__(self) -> str:
        return f"{self.item} ({self.get_type_display()})"

    def get_delta(self) -> int:
        if self.type == self.Type.IN:
            return self.qty
        if self.type in {self.Type.OUT, self.Type.LOSS}:
            return -abs(self.qty)
        return self.qty

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.qty == 0:
            errors["qty"] = "La quantité doit être différente de zéro."
        if self.type in {self.Type.IN, self.Type.OUT, self.Type.LOSS} and self.qty < 0:
            errors["qty"] = "La quantité doit être positive pour ce type."
        if errors:
            raise ValidationError(errors)

        current_stock = self.item.get_stock_from_moves(exclude_move_id=self.pk)
        if current_stock + self.get_delta() < 0:
            raise ValidationError("Stock insuffisant pour cette opération.")

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            InventoryItem.objects.select_for_update().get(pk=self.item_id)
            super().save(*args, **kwargs)
            self.item.refresh_stock_level()

    def delete(self, *args, **kwargs):
        item = self.item
        with transaction.atomic():
            InventoryItem.objects.select_for_update().get(pk=item.pk)
            super().delete(*args, **kwargs)
            item.refresh_stock_level()


class StockLevel(models.Model):
    item = models.OneToOneField(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="stock_level",
        verbose_name="Article",
    )
    quantity = models.IntegerField(default=0, verbose_name="Quantité")
    alert = models.BooleanField(default=False, verbose_name="Alerte stock")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Niveau de stock"
        verbose_name_plural = "Niveaux de stock"

    def __str__(self) -> str:
        return f"{self.item} ({self.quantity})"
