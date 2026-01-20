from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TrainingSector",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=120, unique=True, verbose_name="Secteur"
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
            ],
            options={
                "verbose_name": "Secteur d'activité",
                "verbose_name_plural": "Secteurs d'activité",
            },
        ),
        migrations.CreateModel(
            name="TrainingProgram",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "objective",
                    models.TextField(blank=True, verbose_name="Objectif global"),
                ),
                (
                    "duration_weeks",
                    models.PositiveIntegerField(
                        default=6, verbose_name="Durée (semaines)"
                    ),
                ),
                (
                    "target_role",
                    models.CharField(
                        default="Gestionnaire",
                        max_length=100,
                        verbose_name="Profil ciblé",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Créé le"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Mis à jour le"),
                ),
                (
                    "sectors",
                    models.ManyToManyField(
                        blank=True,
                        related_name="programs",
                        to="training.trainingsector",
                        verbose_name="Secteurs concernés",
                    ),
                ),
            ],
            options={"verbose_name": "Programme", "verbose_name_plural": "Programmes"},
        ),
        migrations.CreateModel(
            name="TrainingWeek",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "week_number",
                    models.PositiveIntegerField(verbose_name="Semaine"),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                ("objective", models.TextField(verbose_name="Objectif")),
                ("focus", models.TextField(blank=True, verbose_name="Axes de travail")),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="weeks",
                        to="training.trainingprogram",
                        verbose_name="Programme",
                    ),
                ),
            ],
            options={
                "verbose_name": "Semaine",
                "verbose_name_plural": "Semaines",
                "ordering": ["week_number"],
            },
        ),
        migrations.CreateModel(
            name="TrainingLesson",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "lesson_type",
                    models.CharField(
                        choices=[
                            ("COURSE", "Cours"),
                            ("WORKSHOP", "Atelier"),
                            ("CHECKLIST", "Checklist"),
                            ("EVALUATION", "Évaluation"),
                        ],
                        default="COURSE",
                        max_length=20,
                        verbose_name="Type",
                    ),
                ),
                (
                    "duration_minutes",
                    models.PositiveIntegerField(default=30, verbose_name="Durée (min)"),
                ),
                (
                    "order",
                    models.PositiveIntegerField(default=1, verbose_name="Ordre"),
                ),
                (
                    "objective",
                    models.TextField(blank=True, verbose_name="Objectif"),
                ),
                (
                    "key_points",
                    models.TextField(blank=True, verbose_name="Points clés"),
                ),
                (
                    "deliverables",
                    models.TextField(blank=True, verbose_name="Livrables"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Créé le"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Mis à jour le"),
                ),
                (
                    "sectors",
                    models.ManyToManyField(
                        blank=True,
                        related_name="lessons",
                        to="training.trainingsector",
                        verbose_name="Secteurs concernés",
                    ),
                ),
                (
                    "week",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lessons",
                        to="training.trainingweek",
                        verbose_name="Semaine",
                    ),
                ),
            ],
            options={
                "verbose_name": "Module",
                "verbose_name_plural": "Modules",
                "ordering": ["week", "order", "id"],
            },
        ),
        migrations.CreateModel(
            name="TrainingLessonChecklistItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(max_length=200, verbose_name="Libellé")),
                (
                    "order",
                    models.PositiveIntegerField(default=0, verbose_name="Ordre"),
                ),
                (
                    "is_required",
                    models.BooleanField(default=True, verbose_name="Obligatoire"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Créé le"),
                ),
                (
                    "lesson",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="checklist_items",
                        to="training.traininglesson",
                        verbose_name="Module",
                    ),
                ),
            ],
            options={
                "verbose_name": "Checklist module",
                "verbose_name_plural": "Checklists module",
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="TrainingLessonResource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "resource_type",
                    models.CharField(
                        choices=[
                            ("GUIDE", "Guide"),
                            ("TEMPLATE", "Template"),
                            ("VIDEO", "Vidéo"),
                            ("CHECKLIST", "Checklist"),
                            ("LINK", "Lien"),
                        ],
                        default="GUIDE",
                        max_length=20,
                        verbose_name="Type",
                    ),
                ),
                ("url", models.URLField(blank=True, verbose_name="Lien")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Créé le"),
                ),
                (
                    "lesson",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resources",
                        to="training.traininglesson",
                        verbose_name="Module",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ressource",
                "verbose_name_plural": "Ressources",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="TrainingEnrollment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "started_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Démarrée le"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("IN_PROGRESS", "En cours"), ("COMPLETED", "Terminée")],
                        default="IN_PROGRESS",
                        max_length=20,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "completed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Terminée le"
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="training.trainingprogram",
                        verbose_name="Programme",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="training_enrollments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Utilisateur",
                    ),
                ),
            ],
            options={
                "verbose_name": "Inscription",
                "verbose_name_plural": "Inscriptions",
                "unique_together": {("user", "program")},
            },
        ),
        migrations.CreateModel(
            name="TrainingEvaluation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.PositiveIntegerField(verbose_name="Score")),
                (
                    "comments",
                    models.TextField(blank=True, verbose_name="Commentaires"),
                ),
                (
                    "evaluated_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Évalué le"),
                ),
                (
                    "enrollment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluation",
                        to="training.trainingenrollment",
                        verbose_name="Inscription",
                    ),
                ),
            ],
            options={
                "verbose_name": "Évaluation",
                "verbose_name_plural": "Évaluations",
            },
        ),
        migrations.CreateModel(
            name="TrainingProgress",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "completed",
                    models.BooleanField(default=False, verbose_name="Terminé"),
                ),
                (
                    "completed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Terminé le"
                    ),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="Notes"),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="progress_items",
                        to="training.trainingenrollment",
                        verbose_name="Inscription",
                    ),
                ),
                (
                    "lesson",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="progress_items",
                        to="training.traininglesson",
                        verbose_name="Module",
                    ),
                ),
            ],
            options={
                "verbose_name": "Progression",
                "verbose_name_plural": "Progressions",
                "unique_together": {("enrollment", "lesson")},
            },
        ),
        migrations.CreateModel(
            name="TrainingChecklistProgress",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_done",
                    models.BooleanField(default=False, verbose_name="Terminé"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Mis à jour le"),
                ),
                (
                    "checklist_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="progress_items",
                        to="training.traininglessonchecklistitem",
                        verbose_name="Checklist",
                    ),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="checklist_progress",
                        to="training.trainingenrollment",
                        verbose_name="Inscription",
                    ),
                ),
            ],
            options={
                "verbose_name": "Progression checklist",
                "verbose_name_plural": "Progressions checklist",
                "unique_together": {("enrollment", "checklist_item")},
            },
        ),
        migrations.CreateModel(
            name="TrainingActionPlan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "due_date",
                    models.DateField(blank=True, null=True, verbose_name="Échéance"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PLANNED", "Planifié"),
                            ("IN_PROGRESS", "En cours"),
                            ("DONE", "Réalisé"),
                        ],
                        default="PLANNED",
                        max_length=20,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Créé le"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Mis à jour le"),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="action_plans",
                        to="training.trainingenrollment",
                        verbose_name="Inscription",
                    ),
                ),
            ],
            options={
                "verbose_name": "Plan d'action",
                "verbose_name_plural": "Plans d'action",
                "ordering": ["due_date", "id"],
            },
        ),
    ]
