from django.conf import settings
from django.db import models
from django.utils import timezone


class TrainingSector(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="Secteur")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Secteur d'activité"
        verbose_name_plural = "Secteurs d'activité"

    def __str__(self) -> str:
        return self.name


class TrainingProgram(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(
        max_length=200, unique=True, null=True, blank=True, verbose_name="Slug"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    objective = models.TextField(blank=True, verbose_name="Objectif global")
    duration_weeks = models.PositiveIntegerField(
        default=6, verbose_name="Durée (semaines)"
    )
    target_role = models.CharField(
        max_length=100,
        default="Gestionnaire",
        verbose_name="Profil ciblé",
    )
    sectors = models.ManyToManyField(
        TrainingSector,
        blank=True,
        related_name="programs",
        verbose_name="Secteurs concernés",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Programme"
        verbose_name_plural = "Programmes"

    def __str__(self) -> str:
        return self.title


class TrainingWeek(models.Model):
    program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.CASCADE,
        related_name="weeks",
        verbose_name="Programme",
    )
    week_number = models.PositiveIntegerField(verbose_name="Semaine")
    title = models.CharField(max_length=200, verbose_name="Titre")
    objective = models.TextField(verbose_name="Objectif")
    focus = models.TextField(blank=True, verbose_name="Axes de travail")

    class Meta:
        verbose_name = "Semaine"
        verbose_name_plural = "Semaines"
        ordering = ["week_number"]

    def __str__(self) -> str:
        return f"Semaine {self.week_number}"


class TrainingLesson(models.Model):
    class LessonType(models.TextChoices):
        COURSE = "COURSE", "Cours"
        WORKSHOP = "WORKSHOP", "Atelier"
        CHECKLIST = "CHECKLIST", "Checklist"
        EVALUATION = "EVALUATION", "Évaluation"

    class CompletionMode(models.TextChoices):
        MANUAL = "MANUAL", "Manuel"
        CHECKLIST_ONLY = "CHECKLIST_ONLY", "Checklist seule"
        QUIZ_ONLY = "QUIZ_ONLY", "Quiz seul"
        CHECKLIST_AND_QUIZ = "CHECKLIST_AND_QUIZ", "Checklist + quiz"
        CHECKLIST_QUIZ_AND_SUBMISSION = (
            "CHECKLIST_QUIZ_AND_SUBMISSION",
            "Checklist + quiz + soumission",
        )

    week = models.ForeignKey(
        TrainingWeek,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Semaine",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    lesson_type = models.CharField(
        max_length=20,
        choices=LessonType.choices,
        default=LessonType.COURSE,
        verbose_name="Type",
    )
    duration_minutes = models.PositiveIntegerField(
        default=30, verbose_name="Durée (min)"
    )
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")
    objective = models.TextField(blank=True, verbose_name="Objectif")
    key_points = models.TextField(blank=True, verbose_name="Points clés")
    deliverables = models.TextField(blank=True, verbose_name="Livrables")
    content_md = models.TextField(blank=True, verbose_name="Contenu (Markdown)")
    content_html = models.TextField(blank=True, verbose_name="Contenu (HTML)")
    case_prompt_md = models.TextField(blank=True, verbose_name="Mini-cas (consigne)")
    video_url = models.URLField(blank=True, null=True, verbose_name="Vidéo (URL)")
    estimated_minutes = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Temps estimé (min)"
    )
    completion_mode = models.CharField(
        max_length=40,
        choices=CompletionMode.choices,
        default=CompletionMode.MANUAL,
        verbose_name="Mode de complétion",
    )
    passing_score = models.PositiveIntegerField(default=70, verbose_name="Score requis")
    sectors = models.ManyToManyField(
        TrainingSector,
        blank=True,
        related_name="lessons",
        verbose_name="Secteurs concernés",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ["week", "order", "id"]

    def __str__(self) -> str:
        return self.title


class TrainingLessonResource(models.Model):
    class ResourceType(models.TextChoices):
        GUIDE = "GUIDE", "Guide"
        TEMPLATE = "TEMPLATE", "Template"
        VIDEO = "VIDEO", "Vidéo"
        CHECKLIST = "CHECKLIST", "Checklist"
        LINK = "LINK", "Lien"

    lesson = models.ForeignKey(
        TrainingLesson,
        on_delete=models.CASCADE,
        related_name="resources",
        verbose_name="Module",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    content_md = models.TextField(blank=True, verbose_name="Contenu (Markdown)")
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.GUIDE,
        verbose_name="Type",
    )
    url = models.URLField(blank=True, verbose_name="Lien")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Ressource"
        verbose_name_plural = "Ressources"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.title


class TrainingStudyMaterial(models.Model):
    class SupportType(models.TextChoices):
        SYNTHESIS = "SYNTHESIS", "Fiche de synthèse"
        PRACTICAL_GUIDE = "PRACTICAL_GUIDE", "Guide pratique"
        REVISION = "REVISION", "Guide de révision"

    lesson = models.ForeignKey(
        TrainingLesson,
        on_delete=models.CASCADE,
        related_name="study_materials",
        verbose_name="Module",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    support_type = models.CharField(
        max_length=30,
        choices=SupportType.choices,
        default=SupportType.SYNTHESIS,
        verbose_name="Type de support",
    )
    content_md = models.TextField(verbose_name="Contenu (Markdown)")
    is_mandatory = models.BooleanField(default=False, verbose_name="Indispensable")
    recommended_before_quiz = models.BooleanField(
        default=False, verbose_name="À étudier avant le quiz"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Support d'étude"
        verbose_name_plural = "Supports d'étude"
        ordering = ["lesson", "support_type", "title", "id"]

    def __str__(self) -> str:
        return f"{self.lesson} - {self.title}"


class TrainingStudyMaterialProgress(models.Model):
    material = models.ForeignKey(
        TrainingStudyMaterial,
        on_delete=models.CASCADE,
        related_name="progress_items",
        verbose_name="Support",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="training_study_progress",
        verbose_name="Utilisateur",
    )
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name="Consulté le")

    class Meta:
        verbose_name = "Progression support"
        verbose_name_plural = "Progressions supports"
        unique_together = ("material", "user")


class TrainingConceptCard(models.Model):
    lesson = models.ForeignKey(
        TrainingLesson,
        on_delete=models.CASCADE,
        related_name="concept_cards",
        verbose_name="Module",
    )
    term = models.CharField(max_length=120, verbose_name="Terme")
    definition_md = models.TextField(verbose_name="Définition (Markdown)")
    floxy_example_md = models.TextField(
        blank=True, verbose_name="Exemple Floxy Made (Markdown)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Carte concept"
        verbose_name_plural = "Cartes concepts"
        ordering = ["lesson", "term", "id"]
        unique_together = ("lesson", "term")

    def __str__(self) -> str:
        return f"{self.lesson} - {self.term}"


class TrainingLessonChecklistItem(models.Model):
    lesson = models.ForeignKey(
        TrainingLesson,
        on_delete=models.CASCADE,
        related_name="checklist_items",
        verbose_name="Module",
    )
    label = models.CharField(max_length=200, verbose_name="Libellé")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    is_required = models.BooleanField(default=True, verbose_name="Obligatoire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Checklist module"
        verbose_name_plural = "Checklists module"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.label


class TrainingQuiz(models.Model):
    lesson = models.OneToOneField(
        TrainingLesson,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="quiz",
        verbose_name="Module",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"

    def __str__(self) -> str:
        return f"Quiz {self.lesson}" if self.lesson else "Quiz"


class TrainingQuestion(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = "MCQ", "QCM"
        TRUE_FALSE = "TRUE_FALSE", "Vrai/Faux"
        OPEN = "OPEN", "Ouverte"

    quiz = models.ForeignKey(
        TrainingQuiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Quiz",
    )
    question_text = models.TextField(verbose_name="Question")
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MCQ,
        verbose_name="Type",
    )
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")
    points = models.PositiveIntegerField(default=1, verbose_name="Points")
    explanation = models.TextField(blank=True, verbose_name="Explication")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ["quiz", "order", "id"]

    def __str__(self) -> str:
        return self.question_text[:60]


class TrainingChoice(models.Model):
    question = models.ForeignKey(
        TrainingQuestion,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Question",
    )
    choice_text = models.TextField(verbose_name="Choix")
    is_correct = models.BooleanField(default=False, verbose_name="Correct")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")

    class Meta:
        verbose_name = "Choix"
        verbose_name_plural = "Choix"
        ordering = ["question", "order", "id"]

    def __str__(self) -> str:
        return self.choice_text[:60]


class TrainingQuizAttempt(models.Model):
    quiz = models.ForeignKey(
        TrainingQuiz,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Quiz",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="training_quiz_attempts",
        verbose_name="Utilisateur",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Démarré le")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Soumis le")
    score_percent = models.PositiveIntegerField(null=True, blank=True, verbose_name="Score %")
    passed = models.BooleanField(default=False, verbose_name="Réussi")

    class Meta:
        verbose_name = "Tentative quiz"
        verbose_name_plural = "Tentatives quiz"
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.user} - {self.quiz}"


class TrainingAnswer(models.Model):
    attempt = models.ForeignKey(
        TrainingQuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Tentative",
    )
    question = models.ForeignKey(
        TrainingQuestion,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Question",
    )
    selected_choice = models.ForeignKey(
        TrainingChoice,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="selected_answers",
        verbose_name="Choix",
    )
    answer_text = models.TextField(blank=True, verbose_name="Réponse libre")
    is_correct = models.BooleanField(null=True, blank=True, verbose_name="Correct")
    points_awarded = models.PositiveIntegerField(default=0, verbose_name="Points attribués")

    class Meta:
        verbose_name = "Réponse quiz"
        verbose_name_plural = "Réponses quiz"
        unique_together = ("attempt", "question")

    def __str__(self) -> str:
        return f"{self.attempt} - {self.question}"


class TrainingSubmission(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Soumis"
        REVIEWED = "REVIEWED", "Corrigé"

    lesson = models.ForeignKey(
        TrainingLesson,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Module",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="training_submissions",
        verbose_name="Utilisateur",
    )
    prompt_md = models.TextField(verbose_name="Consigne")
    submission_text = models.TextField(verbose_name="Soumission")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Soumis le")
    score_percent = models.PositiveIntegerField(null=True, blank=True, verbose_name="Score %")
    reviewer_comment = models.TextField(blank=True, verbose_name="Commentaire")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
        verbose_name="Statut",
    )

    class Meta:
        verbose_name = "Soumission"
        verbose_name_plural = "Soumissions"
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"{self.lesson} - {self.user}"


class TrainingEnrollment(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        COMPLETED = "COMPLETED", "Terminée"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="training_enrollments",
        verbose_name="Utilisateur",
    )
    program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Programme",
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Démarrée le")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        verbose_name="Statut",
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Terminée le"
    )

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ("user", "program")

    def __str__(self) -> str:
        return f"{self.user} - {self.program}"

    def get_progress_percent(self) -> float:
        total_lessons = TrainingLesson.objects.filter(week__program=self.program).count()
        completed = TrainingProgress.objects.filter(
            enrollment=self, completed=True
        ).count()
        return round((completed / total_lessons) * 100, 0) if total_lessons else 0

    def refresh_status(self) -> None:
        total_lessons = TrainingLesson.objects.filter(week__program=self.program).count()
        completed = TrainingProgress.objects.filter(
            enrollment=self, completed=True
        ).count()
        if total_lessons and completed >= total_lessons:
            self.status = self.Status.COMPLETED
            self.completed_at = self.completed_at or timezone.now()
            self.save(update_fields=["status", "completed_at"])


class TrainingProgress(models.Model):
    enrollment = models.ForeignKey(
        TrainingEnrollment,
        on_delete=models.CASCADE,
        related_name="progress_items",
        verbose_name="Inscription",
    )
    lesson = models.ForeignKey(
        TrainingLesson,
        on_delete=models.CASCADE,
        related_name="progress_items",
        verbose_name="Module",
    )
    completed = models.BooleanField(default=False, verbose_name="Terminé")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminé le")
    viewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Vu le")
    quiz_best_score = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Meilleur score quiz (%)"
    )
    quiz_passed = models.BooleanField(default=False, verbose_name="Quiz validé")
    submission_done = models.BooleanField(default=False, verbose_name="Soumission faite")
    notes = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Progression"
        verbose_name_plural = "Progressions"
        unique_together = ("enrollment", "lesson")


class TrainingChecklistProgress(models.Model):
    enrollment = models.ForeignKey(
        TrainingEnrollment,
        on_delete=models.CASCADE,
        related_name="checklist_progress",
        verbose_name="Inscription",
    )
    checklist_item = models.ForeignKey(
        TrainingLessonChecklistItem,
        on_delete=models.CASCADE,
        related_name="progress_items",
        verbose_name="Checklist",
    )
    is_done = models.BooleanField(default=False, verbose_name="Terminé")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Progression checklist"
        verbose_name_plural = "Progressions checklist"
        unique_together = ("enrollment", "checklist_item")


class TrainingEvaluation(models.Model):
    enrollment = models.OneToOneField(
        TrainingEnrollment,
        on_delete=models.CASCADE,
        related_name="evaluation",
        verbose_name="Inscription",
    )
    score = models.PositiveIntegerField(verbose_name="Score")
    comments = models.TextField(blank=True, verbose_name="Commentaires")
    evaluated_at = models.DateTimeField(auto_now_add=True, verbose_name="Évalué le")

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"

    @property
    def is_passed(self) -> bool:
        return self.score >= 70


class TrainingActionPlan(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planifié"
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        DONE = "DONE", "Réalisé"

    enrollment = models.ForeignKey(
        TrainingEnrollment,
        on_delete=models.CASCADE,
        related_name="action_plans",
        verbose_name="Inscription",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    due_date = models.DateField(null=True, blank=True, verbose_name="Échéance")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
        verbose_name="Statut",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Plan d'action"
        verbose_name_plural = "Plans d'action"
        ordering = ["due_date", "id"]

    def __str__(self) -> str:
        return self.title
