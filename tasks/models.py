from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class RecurrenceRule(models.Model):
    class Frequency(models.TextChoices):
        DAILY = "DAILY", "Quotidien"
        WEEKLY = "WEEKLY", "Hebdomadaire"
        MONTHLY = "MONTHLY", "Mensuel"

    name = models.CharField(max_length=150, verbose_name="Nom")
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        verbose_name="Fréquence",
    )
    interval = models.PositiveIntegerField(default=1, verbose_name="Intervalle")
    weekdays = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Jours de la semaine",
        help_text="Numéros 0 (lundi) à 6 (dimanche) séparés par des virgules.",
    )
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Règle de récurrence"
        verbose_name_plural = "Règles de récurrence"

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if not self.weekdays:
            return
        invalid_values = []
        for part in self.weekdays.split(","):
            value = part.strip()
            if not value:
                continue
            if not value.isdigit():
                invalid_values.append(value)
                continue
            day = int(value)
            if day < 0 or day > 6:
                invalid_values.append(value)
        if invalid_values:
            raise ValidationError(
                {"weekdays": "Les jours doivent être compris entre 0 et 6 (lundi=0)."}
            )

    def get_weekdays(self) -> list[int]:
        if not self.weekdays:
            return []
        values = []
        for part in self.weekdays.split(","):
            part = part.strip()
            if part:
                values.append(int(part))
        return sorted(set(values))

    def should_run_on(self, current_date) -> bool:
        weekdays = self.get_weekdays()
        base_date = self.created_at.date() if self.created_at else current_date

        if current_date < base_date:
            return False

        weekday_match = not weekdays or current_date.weekday() in weekdays

        if self.frequency == self.Frequency.DAILY:
            delta_days = (current_date - base_date).days
            return weekday_match and delta_days % self.interval == 0

        if self.frequency == self.Frequency.WEEKLY:
            if not weekdays:
                weekdays = [base_date.weekday()]
            if current_date.weekday() not in weekdays:
                return False
            delta_weeks = (current_date - base_date).days // 7
            return delta_weeks % self.interval == 0

        if self.frequency == self.Frequency.MONTHLY:
            if current_date.day != base_date.day:
                return False
            month_delta = (current_date.year - base_date.year) * 12 + (
                current_date.month - base_date.month
            )
            return weekday_match and month_delta % self.interval == 0

        return False


class TaskTemplate(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    recurrence_rule = models.ForeignKey(
        RecurrenceRule,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="templates",
        verbose_name="Règle de récurrence",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Modèle de tâche"
        verbose_name_plural = "Modèles de tâche"

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "TODO", "À faire"
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        DONE = "DONE", "Terminée"
        CANCELED = "CANCELED", "Annulée"

    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name="Statut",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        verbose_name="Assignée à",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_tasks",
        verbose_name="Créée par",
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Échéance")
    template = models.ForeignKey(
        TaskTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        verbose_name="Modèle",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"

    def __str__(self) -> str:
        return self.title

    def set_status(self, new_status: str, save: bool = True) -> None:
        if new_status not in self.Status.values:
            raise ValidationError("Statut invalide.")
        if self.status == new_status:
            return
        self.status = new_status
        if save:
            self.save(update_fields=["status", "updated_at"])


class TaskChecklistItem(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="checklist_items",
        verbose_name="Tâche",
    )
    label = models.CharField(max_length=200, verbose_name="Libellé")
    is_done = models.BooleanField(default=False, verbose_name="Terminé")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Élément de checklist"
        verbose_name_plural = "Éléments de checklist"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.label


class TaskTemplateChecklist(models.Model):
    template = models.ForeignKey(
        TaskTemplate,
        on_delete=models.CASCADE,
        related_name="checklist_items",
        verbose_name="Modèle",
    )
    label = models.CharField(max_length=200, verbose_name="Libellé")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Checklist de modèle"
        verbose_name_plural = "Checklists de modèle"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.label
