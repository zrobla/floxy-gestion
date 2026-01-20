# Generated manually for LMS schema with UUIDs
import uuid

from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("crm", "0001_initial"),
        ("operations", "0007_merge_20260120_0522"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("objectives", models.TextField(blank=True, verbose_name="Objectifs")),
                (
                    "duration_weeks",
                    models.PositiveIntegerField(default=6, verbose_name="Durée (semaines)"),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Actif")),
            ],
            options={
                "verbose_name": "Cours",
                "verbose_name_plural": "Cours",
                "ordering": ["title"],
            },
        ),
        migrations.CreateModel(
            name="Module",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("week_number", models.PositiveIntegerField(verbose_name="Semaine")),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                ("objective", models.TextField(blank=True, verbose_name="Objectif")),
                ("overview", models.TextField(blank=True, verbose_name="Résumé")),
                ("order", models.PositiveIntegerField(default=1, verbose_name="Ordre")),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="modules",
                        to="lms.course",
                        verbose_name="Cours",
                    ),
                ),
            ],
            options={
                "verbose_name": "Module",
                "verbose_name_plural": "Modules",
                "ordering": ["course", "order", "week_number"],
            },
        ),
        migrations.CreateModel(
            name="Lesson",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("content", models.TextField(blank=True, verbose_name="Contenu")),
                (
                    "lesson_type",
                    models.CharField(
                        choices=[
                            ("COURSE", "Cours"),
                            ("PRACTICE", "Pratique"),
                            ("WORKSHOP", "Atelier"),
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
                ("order", models.PositiveIntegerField(default=1, verbose_name="Ordre")),
                ("is_required", models.BooleanField(default=True, verbose_name="Obligatoire")),
                (
                    "module",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lessons",
                        to="lms.module",
                        verbose_name="Module",
                    ),
                ),
            ],
            options={
                "verbose_name": "Leçon",
                "verbose_name_plural": "Leçons",
                "ordering": ["module", "order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Resource",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                (
                    "resource_type",
                    models.CharField(
                        choices=[
                            ("GUIDE", "Guide"),
                            ("TEMPLATE", "Template"),
                            ("VIDEO", "Vidéo"),
                            ("CHECKLIST", "Checklist"),
                            ("LINK", "Lien"),
                            ("FILE", "Fichier"),
                        ],
                        default="GUIDE",
                        max_length=20,
                        verbose_name="Type",
                    ),
                ),
                ("url", models.URLField(blank=True, verbose_name="Lien")),
                (
                    "file",
                    models.FileField(blank=True, null=True, upload_to="lms/resources/"),
                ),
                ("order", models.PositiveIntegerField(default=1, verbose_name="Ordre")),
                (
                    "lesson",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resources",
                        to="lms.lesson",
                        verbose_name="Leçon",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ressource",
                "verbose_name_plural": "Ressources",
                "ordering": ["lesson", "order", "id"],
            },
        ),
        migrations.CreateModel(
            name="LearningObjective",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("description", models.TextField(verbose_name="Objectif")),
                ("order", models.PositiveIntegerField(default=1, verbose_name="Ordre")),
                (
                    "course",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learning_objectives",
                        to="lms.course",
                        verbose_name="Cours",
                    ),
                ),
                (
                    "lesson",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learning_objectives",
                        to="lms.lesson",
                        verbose_name="Leçon",
                    ),
                ),
                (
                    "module",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learning_objectives",
                        to="lms.module",
                        verbose_name="Module",
                    ),
                ),
            ],
            options={
                "verbose_name": "Objectif pédagogique",
                "verbose_name_plural": "Objectifs pédagogiques",
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ENROLLED", "Inscrit"),
                            ("IN_PROGRESS", "En cours"),
                            ("COMPLETED", "Terminé"),
                        ],
                        default="ENROLLED",
                        max_length=20,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "progress_percent",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=5,
                        verbose_name="Progression (%)",
                    ),
                ),
                ("started_at", models.DateTimeField(auto_now_add=True, verbose_name="Démarrée le")),
                ("completed_at", models.DateTimeField(blank=True, null=True, verbose_name="Terminée le")),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="lms.course",
                        verbose_name="Cours",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lms_enrollments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Utilisateur",
                    ),
                ),
            ],
            options={
                "verbose_name": "Inscription LMS",
                "verbose_name_plural": "Inscriptions LMS",
            },
        ),
        migrations.CreateModel(
            name="Progress",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("completed", models.BooleanField(default=False, verbose_name="Terminé")),
                ("completed_at", models.DateTimeField(blank=True, null=True, verbose_name="Terminé le")),
                ("notes", models.TextField(blank=True, verbose_name="Notes")),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lesson_progress",
                        to="lms.enrollment",
                        verbose_name="Inscription",
                    ),
                ),
                (
                    "lesson",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="progress_items",
                        to="lms.lesson",
                        verbose_name="Leçon",
                    ),
                ),
            ],
            options={
                "verbose_name": "Progression",
                "verbose_name_plural": "Progressions",
            },
        ),
        migrations.CreateModel(
            name="CompletionRule",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                (
                    "require_all_lessons",
                    models.BooleanField(default=True, verbose_name="Toutes les leçons"),
                ),
                (
                    "min_lessons_completed",
                    models.PositiveIntegerField(default=0, verbose_name="Leçons minimales"),
                ),
                (
                    "min_quiz_score",
                    models.PositiveIntegerField(default=0, verbose_name="Score quiz minimum"),
                ),
                (
                    "min_progress_percent",
                    models.PositiveIntegerField(default=100, verbose_name="Progression minimale (%)"),
                ),
                (
                    "require_assignments_approved",
                    models.BooleanField(default=False, verbose_name="Devoirs validés requis"),
                ),
                (
                    "course",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="completion_rule",
                        to="lms.course",
                        verbose_name="Cours",
                    ),
                ),
                (
                    "module",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="completion_rule",
                        to="lms.module",
                        verbose_name="Module",
                    ),
                ),
            ],
            options={
                "verbose_name": "Règle de complétion",
                "verbose_name_plural": "Règles de complétion",
            },
        ),
        migrations.CreateModel(
            name="Quiz",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                (
                    "passing_score",
                    models.PositiveIntegerField(default=70, verbose_name="Score minimum"),
                ),
                (
                    "max_attempts",
                    models.PositiveIntegerField(default=3, verbose_name="Tentatives max"),
                ),
                ("order", models.PositiveIntegerField(default=1, verbose_name="Ordre")),
                ("is_active", models.BooleanField(default=True, verbose_name="Actif")),
                (
                    "lesson",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quizzes",
                        to="lms.lesson",
                        verbose_name="Leçon",
                    ),
                ),
                (
                    "module",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quizzes",
                        to="lms.module",
                        verbose_name="Module",
                    ),
                ),
            ],
            options={
                "verbose_name": "Quiz",
                "verbose_name_plural": "Quiz",
                "ordering": ["title"],
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                (
                    "question_type",
                    models.CharField(
                        choices=[
                            ("MCQ", "QCM"),
                            ("TRUE_FALSE", "Vrai/Faux"),
                            ("SHORT", "Réponse courte"),
                        ],
                        default="MCQ",
                        max_length=20,
                        verbose_name="Type",
                    ),
                ),
                ("prompt", models.TextField(verbose_name="Question")),
                (
                    "points",
                    models.PositiveIntegerField(default=1, verbose_name="Points"),
                ),
                ("order", models.PositiveIntegerField(default=1, verbose_name="Ordre")),
                (
                    "correct_text",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Réponse attendue"
                    ),
                ),
                (
                    "case_sensitive",
                    models.BooleanField(default=False, verbose_name="Sensible à la casse"),
                ),
                (
                    "manual_review_required",
                    models.BooleanField(default=False, verbose_name="Correction manuelle"),
                ),
                (
                    "quiz",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions",
                        to="lms.quiz",
                        verbose_name="Quiz",
                    ),
                ),
            ],
            options={
                "verbose_name": "Question",
                "verbose_name_plural": "Questions",
                "ordering": ["quiz", "order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Choice",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("text", models.CharField(max_length=255, verbose_name="Réponse")),
                ("is_correct", models.BooleanField(default=False, verbose_name="Correcte")),
                ("order", models.PositiveIntegerField(default=1, verbose_name="Ordre")),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="choices",
                        to="lms.question",
                        verbose_name="Question",
                    ),
                ),
            ],
            options={
                "verbose_name": "Choix",
                "verbose_name_plural": "Choix",
                "ordering": ["question", "order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Submission",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("attempt_number", models.PositiveIntegerField(default=1, verbose_name="Tentative")),
                ("submitted_at", models.DateTimeField(auto_now_add=True, verbose_name="Soumis le")),
                (
                    "score",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=6,
                        verbose_name="Score",
                    ),
                ),
                (
                    "max_score",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=6,
                        verbose_name="Score max",
                    ),
                ),
                ("passed", models.BooleanField(default=False, verbose_name="Réussi")),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quiz_submissions",
                        to="lms.enrollment",
                        verbose_name="Inscription",
                    ),
                ),
                (
                    "quiz",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="lms.quiz",
                        verbose_name="Quiz",
                    ),
                ),
            ],
            options={
                "verbose_name": "Soumission quiz",
                "verbose_name_plural": "Soumissions quiz",
            },
        ),
        migrations.CreateModel(
            name="SubmissionAnswer",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("text_answer", models.TextField(blank=True, verbose_name="Réponse texte")),
                ("is_correct", models.BooleanField(default=False, verbose_name="Correcte")),
                (
                    "score_awarded",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=6,
                        verbose_name="Score attribué",
                    ),
                ),
                (
                    "manual_scored",
                    models.BooleanField(default=False, verbose_name="Correction manuelle"),
                ),
                (
                    "reviewed_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="Corrigé le"),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="lms.question",
                        verbose_name="Question",
                    ),
                ),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lms_reviewed_answers",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Corrigé par",
                    ),
                ),
                (
                    "selected_choice",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="selected_in",
                        to="lms.choice",
                        verbose_name="Choix sélectionné",
                    ),
                ),
                (
                    "attempt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="lms.submission",
                        verbose_name="Soumission",
                    ),
                ),
            ],
            options={
                "verbose_name": "Réponse quiz",
                "verbose_name_plural": "Réponses quiz",
            },
        ),
        migrations.CreateModel(
            name="Assignment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("title", models.CharField(max_length=200, verbose_name="Titre")),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("instructions", models.TextField(blank=True, verbose_name="Instructions")),
                ("due_date", models.DateField(blank=True, null=True, verbose_name="Date limite")),
                ("requires_kpi_evidence", models.BooleanField(default=False, verbose_name="KPI requis")),
                ("max_score", models.PositiveIntegerField(default=100, verbose_name="Score max")),
                ("requires_review", models.BooleanField(default=True, verbose_name="Validation requise")),
                (
                    "lesson",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to="lms.lesson",
                        verbose_name="Leçon",
                    ),
                ),
                (
                    "module",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignments",
                        to="lms.module",
                        verbose_name="Module",
                    ),
                ),
            ],
            options={
                "verbose_name": "Devoir terrain",
                "verbose_name_plural": "Devoirs terrain",
                "ordering": ["title"],
            },
        ),
        migrations.CreateModel(
            name="AssignmentSubmission",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("response_text", models.TextField(blank=True, verbose_name="Réponse")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("SUBMITTED", "Soumis"),
                            ("NEEDS_CHANGES", "À corriger"),
                            ("APPROVED", "Validé"),
                        ],
                        default="SUBMITTED",
                        max_length=20,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "score",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=6,
                        null=True,
                        verbose_name="Score",
                    ),
                ),
                (
                    "reviewer_notes",
                    models.TextField(blank=True, verbose_name="Notes de validation"),
                ),
                ("submitted_at", models.DateTimeField(auto_now_add=True, verbose_name="Soumis le")),
                ("reviewed_at", models.DateTimeField(blank=True, null=True, verbose_name="Validé le")),
                (
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="lms.assignment",
                        verbose_name="Devoir",
                    ),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignment_submissions",
                        to="lms.enrollment",
                        verbose_name="Inscription",
                    ),
                ),
            ],
            options={
                "verbose_name": "Soumission devoir",
                "verbose_name_plural": "Soumissions devoir",
            },
        ),
        migrations.CreateModel(
            name="AssignmentKPIRequirement",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("label", models.CharField(max_length=200, verbose_name="Indicateur")),
                ("unit", models.CharField(blank=True, max_length=50, verbose_name="Unité")),
                (
                    "min_value",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="Minimum",
                    ),
                ),
                (
                    "max_value",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="Maximum",
                    ),
                ),
                ("is_required", models.BooleanField(default=True, verbose_name="Obligatoire")),
                ("order", models.PositiveIntegerField(default=1, verbose_name="Ordre")),
                (
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="kpi_requirements",
                        to="lms.assignment",
                        verbose_name="Devoir",
                    ),
                ),
            ],
            options={
                "verbose_name": "KPI requis",
                "verbose_name_plural": "KPI requis",
                "ordering": ["assignment", "order", "id"],
            },
        ),
        migrations.CreateModel(
            name="AssignmentKPIEvidence",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                (
                    "value",
                    models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Valeur"),
                ),
                ("proof_url", models.URLField(blank=True, verbose_name="Preuve (lien)")),
                (
                    "proof_file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="lms/kpi_evidence/",
                        verbose_name="Preuve (fichier)",
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="Notes")),
                (
                    "activity",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="kpi_evidence",
                        to="operations.activity",
                        verbose_name="Activité",
                    ),
                ),
                (
                    "crm_client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="kpi_evidence",
                        to="crm.client",
                        verbose_name="Cliente CRM",
                    ),
                ),
                (
                    "requirement",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="evidence",
                        to="lms.assignmentkpirequirement",
                        verbose_name="KPI requis",
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="kpi_evidence",
                        to="lms.assignmentsubmission",
                        verbose_name="Soumission",
                    ),
                ),
            ],
            options={
                "verbose_name": "Preuve KPI",
                "verbose_name_plural": "Preuves KPI",
            },
        ),
        migrations.CreateModel(
            name="Badge",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("name", models.CharField(max_length=120, verbose_name="Nom")),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("icon", models.CharField(blank=True, max_length=200, verbose_name="Icône")),
                (
                    "rule_type",
                    models.CharField(
                        choices=[
                            ("COURSE_COMPLETED", "Cours terminé"),
                            ("MODULE_COMPLETED", "Module terminé"),
                            ("QUIZ_SCORE", "Score quiz"),
                            ("KPI_TARGET", "Objectif KPI"),
                        ],
                        default="COURSE_COMPLETED",
                        max_length=30,
                        verbose_name="Règle",
                    ),
                ),
                ("min_score", models.PositiveIntegerField(default=0, verbose_name="Seuil score")),
                ("kpi_label", models.CharField(blank=True, max_length=200, verbose_name="KPI cible")),
                (
                    "kpi_min_value",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="KPI minimum",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Actif")),
                (
                    "course",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="badges",
                        to="lms.course",
                        verbose_name="Cours",
                    ),
                ),
                (
                    "module",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="badges",
                        to="lms.module",
                        verbose_name="Module",
                    ),
                ),
            ],
            options={
                "verbose_name": "Badge",
                "verbose_name_plural": "Badges",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="BadgeAward",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("awarded_at", models.DateTimeField(auto_now_add=True, verbose_name="Attribué le")),
                ("notes", models.TextField(blank=True, verbose_name="Notes")),
                (
                    "badge",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="awards",
                        to="lms.badge",
                        verbose_name="Badge",
                    ),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="badge_awards",
                        to="lms.enrollment",
                        verbose_name="Inscription",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="badge_awards",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Utilisateur",
                    ),
                ),
            ],
            options={
                "verbose_name": "Attribution badge",
                "verbose_name_plural": "Attributions badges",
            },
        ),
        migrations.CreateModel(
            name="Certificate",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("certificate_number", models.CharField(max_length=50, unique=True, verbose_name="Numéro")),
                ("issued_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Émis le")),
                (
                    "status",
                    models.CharField(
                        choices=[("ISSUED", "Émis"), ("REVOKED", "Révoqué")],
                        default="ISSUED",
                        max_length=20,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "pdf_file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="lms/certificates/",
                        verbose_name="PDF",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="issued_certificates",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Créé par",
                    ),
                ),
                (
                    "enrollment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="certificate",
                        to="lms.enrollment",
                        verbose_name="Inscription",
                    ),
                ),
            ],
            options={
                "verbose_name": "Certificat",
                "verbose_name_plural": "Certificats",
            },
        ),
        migrations.AddConstraint(
            model_name="module",
            constraint=models.UniqueConstraint(
                fields=("course", "week_number"), name="lms_module_course_week_uniq"
            ),
        ),
        migrations.AddConstraint(
            model_name="learningobjective",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(course__isnull=False, module__isnull=True, lesson__isnull=True)
                    | models.Q(course__isnull=True, module__isnull=False, lesson__isnull=True)
                    | models.Q(course__isnull=True, module__isnull=True, lesson__isnull=False)
                ),
                name="lms_objective_scope_check",
            ),
        ),
        migrations.AddConstraint(
            model_name="enrollment",
            constraint=models.UniqueConstraint(
                fields=("user", "course"), name="lms_enrollment_user_course_uniq"
            ),
        ),
        migrations.AddConstraint(
            model_name="progress",
            constraint=models.UniqueConstraint(
                fields=("enrollment", "lesson"), name="lms_progress_enroll_lesson_uniq"
            ),
        ),
        migrations.AddConstraint(
            model_name="completionrule",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(course__isnull=False, module__isnull=True)
                    | models.Q(course__isnull=True, module__isnull=False)
                ),
                name="lms_completion_scope_check",
            ),
        ),
        migrations.AddConstraint(
            model_name="submission",
            constraint=models.UniqueConstraint(
                fields=("enrollment", "quiz", "attempt_number"),
                name="lms_submission_attempt_uniq",
            ),
        ),
        migrations.AddConstraint(
            model_name="submissionanswer",
            constraint=models.UniqueConstraint(
                fields=("attempt", "question"), name="lms_submission_question_uniq"
            ),
        ),
        migrations.AddConstraint(
            model_name="assignmentsubmission",
            constraint=models.UniqueConstraint(
                fields=("enrollment", "assignment"),
                name="lms_assignment_submission_uniq",
            ),
        ),
        migrations.AddConstraint(
            model_name="badgeaward",
            constraint=models.UniqueConstraint(
                fields=("badge", "user"), name="lms_badge_user_uniq"
            ),
        ),
        migrations.AddIndex(
            model_name="course",
            index=models.Index(fields=["slug"], name="lms_course_slug_idx"),
        ),
        migrations.AddIndex(
            model_name="course",
            index=models.Index(fields=["is_active"], name="lms_course_active_idx"),
        ),
        migrations.AddIndex(
            model_name="module",
            index=models.Index(fields=["course", "order"], name="lms_module_order_idx"),
        ),
        migrations.AddIndex(
            model_name="module",
            index=models.Index(fields=["course", "week_number"], name="lms_module_week_idx"),
        ),
        migrations.AddIndex(
            model_name="lesson",
            index=models.Index(fields=["module", "order"], name="lms_lesson_order_idx"),
        ),
        migrations.AddIndex(
            model_name="lesson",
            index=models.Index(fields=["lesson_type"], name="lms_lesson_type_idx"),
        ),
        migrations.AddIndex(
            model_name="resource",
            index=models.Index(fields=["lesson", "order"], name="lms_resource_order_idx"),
        ),
        migrations.AddIndex(
            model_name="resource",
            index=models.Index(fields=["resource_type"], name="lms_resource_type_idx"),
        ),
        migrations.AddIndex(
            model_name="learningobjective",
            index=models.Index(fields=["course"], name="lms_objective_course_idx"),
        ),
        migrations.AddIndex(
            model_name="learningobjective",
            index=models.Index(fields=["module"], name="lms_objective_module_idx"),
        ),
        migrations.AddIndex(
            model_name="learningobjective",
            index=models.Index(fields=["lesson"], name="lms_objective_lesson_idx"),
        ),
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(fields=["user"], name="lms_enroll_user_idx"),
        ),
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(fields=["course"], name="lms_enroll_course_idx"),
        ),
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(fields=["status"], name="lms_enroll_status_idx"),
        ),
        migrations.AddIndex(
            model_name="progress",
            index=models.Index(fields=["enrollment"], name="lms_progress_enroll_idx"),
        ),
        migrations.AddIndex(
            model_name="progress",
            index=models.Index(fields=["completed"], name="lms_progress_completed_idx"),
        ),
        migrations.AddIndex(
            model_name="completionrule",
            index=models.Index(fields=["course"], name="lms_completion_course_idx"),
        ),
        migrations.AddIndex(
            model_name="completionrule",
            index=models.Index(fields=["module"], name="lms_completion_module_idx"),
        ),
        migrations.AddIndex(
            model_name="quiz",
            index=models.Index(fields=["lesson"], name="lms_quiz_lesson_idx"),
        ),
        migrations.AddIndex(
            model_name="quiz",
            index=models.Index(fields=["module"], name="lms_quiz_module_idx"),
        ),
        migrations.AddIndex(
            model_name="quiz",
            index=models.Index(fields=["is_active"], name="lms_quiz_active_idx"),
        ),
        migrations.AddIndex(
            model_name="question",
            index=models.Index(fields=["quiz", "order"], name="lms_question_order_idx"),
        ),
        migrations.AddIndex(
            model_name="choice",
            index=models.Index(fields=["question", "order"], name="lms_choice_order_idx"),
        ),
        migrations.AddIndex(
            model_name="choice",
            index=models.Index(fields=["is_correct"], name="lms_choice_correct_idx"),
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(fields=["quiz"], name="lms_submission_quiz_idx"),
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(fields=["passed"], name="lms_submission_passed_idx"),
        ),
        migrations.AddIndex(
            model_name="submissionanswer",
            index=models.Index(fields=["attempt"], name="lms_answer_submission_idx"),
        ),
        migrations.AddIndex(
            model_name="assignment",
            index=models.Index(fields=["due_date"], name="lms_assignment_due_idx"),
        ),
        migrations.AddIndex(
            model_name="assignment",
            index=models.Index(
                fields=["requires_kpi_evidence"], name="lms_assignment_kpi_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="assignmentsubmission",
            index=models.Index(fields=["status"], name="lms_assignment_status_idx"),
        ),
        migrations.AddIndex(
            model_name="assignmentkpirequirement",
            index=models.Index(fields=["assignment", "order"], name="lms_kpi_order_idx"),
        ),
        migrations.AddIndex(
            model_name="assignmentkpievidence",
            index=models.Index(fields=["submission"], name="lms_kpi_submission_idx"),
        ),
        migrations.AddIndex(
            model_name="badge",
            index=models.Index(fields=["rule_type"], name="lms_badge_rule_idx"),
        ),
        migrations.AddIndex(
            model_name="badge",
            index=models.Index(fields=["is_active"], name="lms_badge_active_idx"),
        ),
        migrations.AddIndex(
            model_name="badgeaward",
            index=models.Index(fields=["badge"], name="lms_badge_award_idx"),
        ),
        migrations.AddIndex(
            model_name="badgeaward",
            index=models.Index(fields=["user"], name="lms_badge_user_idx"),
        ),
        migrations.AddIndex(
            model_name="certificate",
            index=models.Index(fields=["status"], name="lms_cert_status_idx"),
        ),
        migrations.AddIndex(
            model_name="certificate",
            index=models.Index(fields=["issued_at"], name="lms_cert_issued_idx"),
        ),
    ]
