from __future__ import annotations

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify


class UUIDTimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        abstract = True


class Course(UUIDTimeStampedModel):
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    objectives = models.TextField(blank=True, verbose_name="Objectifs")
    duration_weeks = models.PositiveIntegerField(default=6, verbose_name="Durée (semaines)")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ["title"]
        indexes = [
            models.Index(fields=["slug"], name="lms_course_slug_idx"),
            models.Index(fields=["is_active"], name="lms_course_active_idx"),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)


class Module(UUIDTimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name="Cours",
    )
    week_number = models.PositiveIntegerField(verbose_name="Semaine")
    title = models.CharField(max_length=200, verbose_name="Titre")
    objective = models.TextField(blank=True, verbose_name="Objectif")
    overview = models.TextField(blank=True, verbose_name="Résumé")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ["course", "order", "week_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "week_number"], name="lms_module_course_week_uniq"
            )
        ]
        indexes = [
            models.Index(fields=["course", "order"], name="lms_module_order_idx"),
            models.Index(fields=["course", "week_number"], name="lms_module_week_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.course} - S{self.week_number}"


class Lesson(UUIDTimeStampedModel):
    class LessonType(models.TextChoices):
        COURSE = "COURSE", "Cours"
        PRACTICE = "PRACTICE", "Pratique"
        WORKSHOP = "WORKSHOP", "Atelier"
        EVALUATION = "EVALUATION", "Évaluation"

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Module",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    content = models.TextField(blank=True, verbose_name="Contenu")
    lesson_type = models.CharField(
        max_length=20,
        choices=LessonType.choices,
        default=LessonType.COURSE,
        verbose_name="Type",
    )
    duration_minutes = models.PositiveIntegerField(default=30, verbose_name="Durée (min)")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")
    is_required = models.BooleanField(default=True, verbose_name="Obligatoire")

    class Meta:
        verbose_name = "Leçon"
        verbose_name_plural = "Leçons"
        ordering = ["module", "order", "id"]
        indexes = [
            models.Index(fields=["module", "order"], name="lms_lesson_order_idx"),
            models.Index(fields=["lesson_type"], name="lms_lesson_type_idx"),
        ]

    def __str__(self) -> str:
        return self.title


class Resource(UUIDTimeStampedModel):
    class ResourceType(models.TextChoices):
        GUIDE = "GUIDE", "Guide"
        TEMPLATE = "TEMPLATE", "Template"
        VIDEO = "VIDEO", "Vidéo"
        CHECKLIST = "CHECKLIST", "Checklist"
        LINK = "LINK", "Lien"
        FILE = "FILE", "Fichier"

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="resources",
        verbose_name="Leçon",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.GUIDE,
        verbose_name="Type",
    )
    url = models.URLField(blank=True, verbose_name="Lien")
    file = models.FileField(upload_to="lms/resources/", blank=True, null=True)
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")

    class Meta:
        verbose_name = "Ressource"
        verbose_name_plural = "Ressources"
        ordering = ["lesson", "order", "id"]
        indexes = [
            models.Index(fields=["lesson", "order"], name="lms_resource_order_idx"),
            models.Index(fields=["resource_type"], name="lms_resource_type_idx"),
        ]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        if not self.url and not self.file:
            raise ValidationError("Un lien ou un fichier est requis pour la ressource.")


class LearningObjective(UUIDTimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="learning_objectives",
        null=True,
        blank=True,
        verbose_name="Cours",
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="learning_objectives",
        null=True,
        blank=True,
        verbose_name="Module",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="learning_objectives",
        null=True,
        blank=True,
        verbose_name="Leçon",
    )
    description = models.TextField(verbose_name="Objectif")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")

    class Meta:
        verbose_name = "Objectif pédagogique"
        verbose_name_plural = "Objectifs pédagogiques"
        ordering = ["order", "id"]
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(course__isnull=False, module__isnull=True, lesson__isnull=True)
                    | Q(course__isnull=True, module__isnull=False, lesson__isnull=True)
                    | Q(course__isnull=True, module__isnull=True, lesson__isnull=False)
                ),
                name="lms_objective_scope_check",
            )
        ]
        indexes = [
            models.Index(fields=["course"], name="lms_objective_course_idx"),
            models.Index(fields=["module"], name="lms_objective_module_idx"),
            models.Index(fields=["lesson"], name="lms_objective_lesson_idx"),
        ]

    def __str__(self) -> str:
        return self.description[:60]


class Enrollment(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        ENROLLED = "ENROLLED", "Inscrit"
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        COMPLETED = "COMPLETED", "Terminé"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lms_enrollments",
        verbose_name="Utilisateur",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Cours",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ENROLLED,
        verbose_name="Statut",
    )
    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Progression (%)",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Démarrée le")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminée le")

    class Meta:
        verbose_name = "Inscription LMS"
        verbose_name_plural = "Inscriptions LMS"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="lms_enrollment_user_course_uniq"
            )
        ]
        indexes = [
            models.Index(fields=["user"], name="lms_enroll_user_idx"),
            models.Index(fields=["course"], name="lms_enroll_course_idx"),
            models.Index(fields=["status"], name="lms_enroll_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.course}"


class Progress(UUIDTimeStampedModel):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
        verbose_name="Inscription",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progress_items",
        verbose_name="Leçon",
    )
    completed = models.BooleanField(default=False, verbose_name="Terminé")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminé le")
    viewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Vu le")
    quiz_passed = models.BooleanField(default=False, verbose_name="Quiz validé")
    notes = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Progression"
        verbose_name_plural = "Progressions"
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson"], name="lms_progress_enroll_lesson_uniq"
            )
        ]
        indexes = [
            models.Index(fields=["enrollment"], name="lms_progress_enroll_idx"),
            models.Index(fields=["completed"], name="lms_progress_completed_idx"),
        ]


class CompletionRule(UUIDTimeStampedModel):
    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name="completion_rule",
        null=True,
        blank=True,
        verbose_name="Cours",
    )
    module = models.OneToOneField(
        Module,
        on_delete=models.CASCADE,
        related_name="completion_rule",
        null=True,
        blank=True,
        verbose_name="Module",
    )
    require_all_lessons = models.BooleanField(default=True, verbose_name="Toutes les leçons")
    min_lessons_completed = models.PositiveIntegerField(
        default=0,
        verbose_name="Leçons minimales",
    )
    min_quiz_score = models.PositiveIntegerField(
        default=0,
        verbose_name="Score quiz minimum",
    )
    min_progress_percent = models.PositiveIntegerField(
        default=100,
        verbose_name="Progression minimale (%)",
    )
    require_assignments_approved = models.BooleanField(
        default=False,
        verbose_name="Devoirs validés requis",
    )

    class Meta:
        verbose_name = "Règle de complétion"
        verbose_name_plural = "Règles de complétion"
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(course__isnull=False, module__isnull=True)
                    | Q(course__isnull=True, module__isnull=False)
                ),
                name="lms_completion_scope_check",
            )
        ]
        indexes = [
            models.Index(fields=["course"], name="lms_completion_course_idx"),
            models.Index(fields=["module"], name="lms_completion_module_idx"),
        ]

    def __str__(self) -> str:
        scope = self.course or self.module
        return f"Règle - {scope}"


class Quiz(UUIDTimeStampedModel):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="quizzes",
        verbose_name="Leçon",
        null=True,
        blank=True,
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="quizzes",
        verbose_name="Module",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    passing_score = models.PositiveIntegerField(default=70, verbose_name="Score minimum")
    max_attempts = models.PositiveIntegerField(default=3, verbose_name="Tentatives max")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_required_for_completion = models.BooleanField(
        default=False, verbose_name="Requis pour la complétion"
    )

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"
        ordering = ["title"]
        indexes = [
            models.Index(fields=["lesson"], name="lms_quiz_lesson_idx"),
            models.Index(fields=["module"], name="lms_quiz_module_idx"),
            models.Index(fields=["is_active"], name="lms_quiz_active_idx"),
        ]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        if not self.lesson and not self.module:
            raise ValidationError("Un quiz doit être lié à une leçon ou un module.")
        if self.lesson and self.module and self.lesson.module_id != self.module_id:
            raise ValidationError("Le module doit correspondre à la leçon sélectionnée.")


class Question(UUIDTimeStampedModel):
    class QuestionType(models.TextChoices):
        MCQ = "MCQ", "QCM"
        TRUE_FALSE = "TRUE_FALSE", "Vrai/Faux"
        SHORT = "SHORT", "Réponse courte"

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Quiz",
    )
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MCQ,
        verbose_name="Type",
    )
    prompt = models.TextField(verbose_name="Question")
    points = models.PositiveIntegerField(default=1, verbose_name="Points")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")
    correct_text = models.CharField(max_length=255, blank=True, verbose_name="Réponse attendue")
    case_sensitive = models.BooleanField(default=False, verbose_name="Sensible à la casse")
    manual_review_required = models.BooleanField(
        default=False, verbose_name="Correction manuelle"
    )

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ["quiz", "order", "id"]
        indexes = [
            models.Index(fields=["quiz", "order"], name="lms_question_order_idx"),
        ]

    def __str__(self) -> str:
        return self.prompt[:60]


class Choice(UUIDTimeStampedModel):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Question",
    )
    text = models.CharField(max_length=255, verbose_name="Réponse")
    is_correct = models.BooleanField(default=False, verbose_name="Correcte")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")

    class Meta:
        verbose_name = "Choix"
        verbose_name_plural = "Choix"
        ordering = ["question", "order", "id"]
        indexes = [
            models.Index(fields=["question", "order"], name="lms_choice_order_idx"),
            models.Index(fields=["is_correct"], name="lms_choice_correct_idx"),
        ]

    def __str__(self) -> str:
        return self.text


class Submission(UUIDTimeStampedModel):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="quiz_submissions",
        verbose_name="Inscription",
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Quiz",
    )
    attempt_number = models.PositiveIntegerField(default=1, verbose_name="Tentative")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Soumis le")
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Score",
    )
    max_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Score max",
    )
    passed = models.BooleanField(default=False, verbose_name="Réussi")

    class Meta:
        verbose_name = "Soumission quiz"
        verbose_name_plural = "Soumissions quiz"
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "quiz", "attempt_number"],
                name="lms_submission_attempt_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["quiz"], name="lms_submission_quiz_idx"),
            models.Index(fields=["passed"], name="lms_submission_passed_idx"),
        ]


class SubmissionAnswer(UUIDTimeStampedModel):
    attempt = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Soumission",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Question",
    )
    selected_choice = models.ForeignKey(
        Choice,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="selected_in",
        verbose_name="Choix sélectionné",
    )
    text_answer = models.TextField(blank=True, verbose_name="Réponse texte")
    is_correct = models.BooleanField(default=False, verbose_name="Correcte")
    score_awarded = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Score attribué",
    )
    manual_scored = models.BooleanField(default=False, verbose_name="Correction manuelle")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Corrigé le")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lms_reviewed_answers",
        verbose_name="Corrigé par",
    )

    class Meta:
        verbose_name = "Réponse quiz"
        verbose_name_plural = "Réponses quiz"
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"], name="lms_submission_question_uniq"
            )
        ]
        indexes = [
            models.Index(fields=["attempt"], name="lms_answer_submission_idx"),
        ]


class Assignment(UUIDTimeStampedModel):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Leçon",
        null=True,
        blank=True,
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Module",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    instructions = models.TextField(blank=True, verbose_name="Instructions")
    due_date = models.DateField(null=True, blank=True, verbose_name="Date limite")
    requires_kpi_evidence = models.BooleanField(default=False, verbose_name="KPI requis")
    max_score = models.PositiveIntegerField(default=100, verbose_name="Score max")
    requires_review = models.BooleanField(default=True, verbose_name="Validation requise")
    is_final_assessment = models.BooleanField(
        default=False, verbose_name="Évaluation finale"
    )

    class Meta:
        verbose_name = "Devoir terrain"
        verbose_name_plural = "Devoirs terrain"
        ordering = ["title"]
        indexes = [
            models.Index(fields=["due_date"], name="lms_assignment_due_idx"),
            models.Index(fields=["requires_kpi_evidence"], name="lms_assignment_kpi_idx"),
            models.Index(fields=["is_final_assessment"], name="lms_assignment_final_idx"),
        ]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        if not self.lesson and not self.module:
            raise ValidationError("Un devoir doit être lié à une leçon ou un module.")
        if self.lesson and self.module and self.lesson.module_id != self.module_id:
            raise ValidationError("Le module doit correspondre à la leçon sélectionnée.")


class AssignmentSubmission(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Soumis"
        REJECTED = "REJECTED", "Rejeté"
        APPROVED = "APPROVED", "Validé"

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
        verbose_name="Inscription",
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Devoir",
    )
    response_text = models.TextField(blank=True, verbose_name="Réponse")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
        verbose_name="Statut",
    )
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Score",
    )
    feedback = models.TextField(blank=True, verbose_name="Feedback")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Soumis le")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Validé le")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lms_reviewed_assignments",
        verbose_name="Validé par",
    )

    class Meta:
        verbose_name = "Soumission devoir"
        verbose_name_plural = "Soumissions devoir"
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "assignment"],
                name="lms_assignment_submission_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["status"], name="lms_assignment_status_idx"),
        ]


class AssignmentSubmissionAttachment(UUIDTimeStampedModel):
    submission = models.ForeignKey(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Soumission",
    )
    image = models.ImageField(
        upload_to="lms/assignment_attachments/",
        verbose_name="Image",
    )
    caption = models.CharField(max_length=255, blank=True, verbose_name="Légende")

    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"
        indexes = [
            models.Index(fields=["submission"], name="lms_submission_attach_idx"),
        ]


class AssignmentSubmissionLink(UUIDTimeStampedModel):
    submission = models.ForeignKey(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name="proof_links",
        verbose_name="Soumission",
    )
    url = models.URLField(verbose_name="Lien de preuve")
    label = models.CharField(max_length=200, blank=True, verbose_name="Libellé")

    class Meta:
        verbose_name = "Lien de preuve"
        verbose_name_plural = "Liens de preuve"
        indexes = [
            models.Index(fields=["submission"], name="lms_submission_link_idx"),
        ]


class AssignmentSubmissionKPI(UUIDTimeStampedModel):
    submission = models.ForeignKey(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name="kpi_values",
        verbose_name="Soumission",
    )
    label = models.CharField(max_length=200, verbose_name="KPI")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valeur")
    unit = models.CharField(max_length=50, blank=True, verbose_name="Unité")

    class Meta:
        verbose_name = "KPI soumission"
        verbose_name_plural = "KPIs soumission"
        indexes = [
            models.Index(fields=["submission"], name="lms_submission_kpi_idx"),
        ]


class AssignmentKPIRequirement(UUIDTimeStampedModel):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="kpi_requirements",
        verbose_name="Devoir",
    )
    label = models.CharField(max_length=200, verbose_name="Indicateur")
    unit = models.CharField(max_length=50, blank=True, verbose_name="Unité")
    min_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Minimum",
    )
    max_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Maximum",
    )
    is_required = models.BooleanField(default=True, verbose_name="Obligatoire")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")

    class Meta:
        verbose_name = "KPI requis"
        verbose_name_plural = "KPI requis"
        ordering = ["assignment", "order", "id"]
        indexes = [
            models.Index(fields=["assignment", "order"], name="lms_kpi_order_idx"),
        ]

    def __str__(self) -> str:
        return self.label


class AssignmentKPIEvidence(UUIDTimeStampedModel):
    submission = models.ForeignKey(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name="kpi_evidence",
        verbose_name="Soumission",
    )
    requirement = models.ForeignKey(
        AssignmentKPIRequirement,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="evidence",
        verbose_name="KPI requis",
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valeur",
    )
    proof_url = models.URLField(blank=True, verbose_name="Preuve (lien)")
    proof_file = models.FileField(
        upload_to="lms/kpi_evidence/",
        blank=True,
        null=True,
        verbose_name="Preuve (fichier)",
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    crm_client = models.ForeignKey(
        "crm.Client",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="kpi_evidence",
        verbose_name="Cliente CRM",
    )
    activity = models.ForeignKey(
        "operations.Activity",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="kpi_evidence",
        verbose_name="Activité",
    )

    class Meta:
        verbose_name = "Preuve KPI"
        verbose_name_plural = "Preuves KPI"
        indexes = [
            models.Index(fields=["submission"], name="lms_kpi_submission_idx"),
        ]

    def clean(self) -> None:
        super().clean()
        if not self.proof_url and not self.proof_file:
            raise ValidationError("Une preuve (lien ou fichier) est requise.")


class Badge(UUIDTimeStampedModel):
    class RuleType(models.TextChoices):
        COURSE_COMPLETED = "COURSE_COMPLETED", "Cours terminé"
        MODULE_COMPLETED = "MODULE_COMPLETED", "Module terminé"
        QUIZ_SCORE = "QUIZ_SCORE", "Score quiz"
        KPI_TARGET = "KPI_TARGET", "Objectif KPI"
        ASSIGNMENT_APPROVED = "ASSIGNMENT_APPROVED", "Devoir validé"

    name = models.CharField(max_length=120, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    icon = models.CharField(max_length=200, blank=True, verbose_name="Icône")
    rule_type = models.CharField(
        max_length=30,
        choices=RuleType.choices,
        default=RuleType.COURSE_COMPLETED,
        verbose_name="Règle",
    )
    course = models.ForeignKey(
        Course,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="badges",
        verbose_name="Cours",
    )
    module = models.ForeignKey(
        Module,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="badges",
        verbose_name="Module",
    )
    assignment = models.ForeignKey(
        "Assignment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="badges",
        verbose_name="Devoir",
    )
    min_score = models.PositiveIntegerField(default=0, verbose_name="Seuil score")
    kpi_label = models.CharField(max_length=200, blank=True, verbose_name="KPI cible")
    kpi_min_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="KPI minimum",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["rule_type"], name="lms_badge_rule_idx"),
            models.Index(fields=["is_active"], name="lms_badge_active_idx"),
            models.Index(fields=["assignment"], name="lms_badge_assignment_idx"),
        ]

    def __str__(self) -> str:
        return self.name


class BadgeAward(UUIDTimeStampedModel):
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name="awards",
        verbose_name="Badge",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="badge_awards",
        verbose_name="Utilisateur",
    )
    enrollment = models.ForeignKey(
        Enrollment,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="badge_awards",
        verbose_name="Inscription",
    )
    awarded_at = models.DateTimeField(auto_now_add=True, verbose_name="Attribué le")
    notes = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Attribution badge"
        verbose_name_plural = "Attributions badges"
        constraints = [
            models.UniqueConstraint(
                fields=["badge", "user"], name="lms_badge_user_uniq"
            )
        ]
        indexes = [
            models.Index(fields=["badge"], name="lms_badge_award_idx"),
            models.Index(fields=["user"], name="lms_badge_user_idx"),
        ]


class Certificate(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        ISSUED = "ISSUED", "Émis"
        REVOKED = "REVOKED", "Révoqué"

    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="certificate",
        verbose_name="Inscription",
    )
    certificate_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro")
    issued_at = models.DateTimeField(default=timezone.now, verbose_name="Émis le")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ISSUED,
        verbose_name="Statut",
    )
    pdf_file = models.FileField(
        upload_to="lms/certificates/",
        null=True,
        blank=True,
        verbose_name="PDF",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="issued_certificates",
        verbose_name="Créé par",
    )

    class Meta:
        verbose_name = "Certificat"
        verbose_name_plural = "Certificats"
        indexes = [
            models.Index(fields=["status"], name="lms_cert_status_idx"),
            models.Index(fields=["issued_at"], name="lms_cert_issued_idx"),
        ]

    def __str__(self) -> str:
        return self.certificate_number


class CourseModule(Module):
    class Meta:
        proxy = True
        verbose_name = "Module"
        verbose_name_plural = "Modules"


class LessonResource(Resource):
    class Meta:
        proxy = True
        verbose_name = "Ressource"
        verbose_name_plural = "Ressources"


class LessonProgress(Progress):
    class Meta:
        proxy = True
        verbose_name = "Progression"
        verbose_name_plural = "Progressions"


class QuizQuestion(Question):
    class Meta:
        proxy = True
        verbose_name = "Question"
        verbose_name_plural = "Questions"


class QuizChoice(Choice):
    class Meta:
        proxy = True
        verbose_name = "Choix"
        verbose_name_plural = "Choix"


class QuizAttempt(Submission):
    class Meta:
        proxy = True
        verbose_name = "Soumission quiz"
        verbose_name_plural = "Soumissions quiz"


class QuizAnswer(SubmissionAnswer):
    class Meta:
        proxy = True
        verbose_name = "Réponse quiz"
        verbose_name_plural = "Réponses quiz"


class ModuleCompletionRuleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(module__isnull=False)


class CourseCompletionRuleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(course__isnull=False)


class ModuleCompletionRule(CompletionRule):
    objects = ModuleCompletionRuleManager()

    class Meta:
        proxy = True
        verbose_name = "Règle module"
        verbose_name_plural = "Règles module"


class CourseCompletionRule(CompletionRule):
    objects = CourseCompletionRuleManager()

    class Meta:
        proxy = True
        verbose_name = "Règle cours"
        verbose_name_plural = "Règles cours"
