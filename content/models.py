from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ContentItem(models.Model):
    class Status(models.TextChoices):
        IDEA = "IDEA", "Idée"
        BRIEF = "BRIEF", "Brief"
        IN_CREATION = "IN_CREATION", "En création"
        TO_VALIDATE = "TO_VALIDATE", "À valider"
        APPROVED = "APPROVED", "Validé"
        SCHEDULED = "SCHEDULED", "Programmé"
        PUBLISHED = "PUBLISHED", "Publié"
        METRICS_RECORDED = "METRICS_RECORDED", "Résultats saisis"
        REJECTED = "REJECTED", "Refusé"

    class Platform(models.TextChoices):
        INSTAGRAM = "INSTAGRAM", "Instagram"
        TIKTOK = "TIKTOK", "TikTok"
        FACEBOOK = "FACEBOOK", "Facebook"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        YOUTUBE = "YOUTUBE", "YouTube"
        OTHER = "OTHER", "Autre"

    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.IDEA,
        verbose_name="Statut",
    )
    platform = models.CharField(
        max_length=20,
        choices=Platform.choices,
        default=Platform.INSTAGRAM,
        verbose_name="Plateforme",
    )
    scheduled_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Date de publication"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="content_items",
        verbose_name="Créé par",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_content_items",
        verbose_name="Validé par",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Contenu"
        verbose_name_plural = "Contenus"

    def __str__(self) -> str:
        return self.title

    def submit_for_approval(self) -> None:
        if self.status not in {self.Status.IN_CREATION, self.Status.BRIEF}:
            raise ValidationError("Le contenu n'est pas prêt pour validation.")
        self.status = self.Status.TO_VALIDATE
        self.save(update_fields=["status", "updated_at"])

    def approve(self, user, comment: str) -> None:
        if self.status != self.Status.TO_VALIDATE:
            raise ValidationError("Le contenu doit être en attente de validation.")
        if not comment:
            raise ValidationError("Un commentaire est requis pour valider.")
        self.status = self.Status.APPROVED
        self.approved_by = user
        self.save(update_fields=["status", "approved_by", "updated_at"])

    def reject(self, user, comment: str) -> None:
        if self.status != self.Status.TO_VALIDATE:
            raise ValidationError("Le contenu doit être en attente de validation.")
        if not comment:
            raise ValidationError("Un commentaire est requis pour refuser.")
        self.status = self.Status.IN_CREATION
        self.approved_by = user
        self.save(update_fields=["status", "approved_by", "updated_at"])

    def publish(self) -> None:
        if self.status not in {self.Status.APPROVED, self.Status.SCHEDULED}:
            raise ValidationError("Le contenu doit être validé ou programmé.")
        self.status = self.Status.PUBLISHED
        self.save(update_fields=["status", "updated_at"])

    def record_metrics(self) -> None:
        if self.status != self.Status.PUBLISHED:
            raise ValidationError("Le contenu doit être publié avant les résultats.")
        self.status = self.Status.METRICS_RECORDED
        self.save(update_fields=["status", "updated_at"])

    def get_performance_score(self) -> float:
        metric = self.metrics.order_by("-created_at").first()
        if not metric:
            return 0.0
        return metric.performance_score


class ContentApproval(models.Model):
    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="approvals",
        verbose_name="Contenu",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="content_approvals",
        verbose_name="Validé par",
    )
    comment = models.TextField(verbose_name="Commentaire")
    approved = models.BooleanField(default=False, verbose_name="Validé")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Validation de contenu"
        verbose_name_plural = "Validations de contenu"


class ContentMetric(models.Model):
    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="metrics",
        verbose_name="Contenu",
    )
    likes = models.PositiveIntegerField(default=0, verbose_name="Likes")
    comments = models.PositiveIntegerField(default=0, verbose_name="Commentaires")
    shares = models.PositiveIntegerField(default=0, verbose_name="Partages")
    saves = models.PositiveIntegerField(default=0, verbose_name="Enregistrements")
    reach = models.PositiveIntegerField(default=0, verbose_name="Portée")
    clicks = models.PositiveIntegerField(default=0, verbose_name="Clics")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Métrique de contenu"
        verbose_name_plural = "Métriques de contenu"

    @property
    def performance_score(self) -> float:
        interactions = self.likes + self.comments + self.shares + self.saves
        if self.reach <= 0:
            return float(interactions)
        return round((interactions / self.reach) * 100, 2)
