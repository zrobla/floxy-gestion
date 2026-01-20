from django.contrib import admin
from django.utils import timezone

from lms import models
from lms.services.quiz import compute_score


class ResourceInline(admin.TabularInline):
    model = models.Resource
    extra = 0


class LessonInline(admin.TabularInline):
    model = models.Lesson
    extra = 0


class LearningObjectiveInline(admin.TabularInline):
    model = models.LearningObjective
    extra = 0


class QuestionInline(admin.TabularInline):
    model = models.Question
    extra = 0


class ChoiceInline(admin.TabularInline):
    model = models.Choice
    extra = 0


class AssignmentKPIInline(admin.TabularInline):
    model = models.AssignmentKPIRequirement
    extra = 0


class AssignmentKPIEvidenceInline(admin.TabularInline):
    model = models.AssignmentKPIEvidence
    extra = 0


class AssignmentAttachmentInline(admin.TabularInline):
    model = models.AssignmentSubmissionAttachment
    extra = 0


class AssignmentLinkInline(admin.TabularInline):
    model = models.AssignmentSubmissionLink
    extra = 0


class AssignmentKPIValueInline(admin.TabularInline):
    model = models.AssignmentSubmissionKPI
    extra = 0


class SubmissionAnswerInline(admin.TabularInline):
    model = models.SubmissionAnswer
    extra = 0
    fields = (
        "question",
        "selected_choice",
        "text_answer",
        "is_correct",
        "score_awarded",
        "manual_scored",
        "reviewed_at",
        "reviewed_by",
    )
    readonly_fields = ("question", "selected_choice", "text_answer", "reviewed_at", "reviewed_by")


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_weeks", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "description")


@admin.register(models.Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("course", "week_number", "title", "order")
    list_filter = ("course",)
    search_fields = ("title",)
    ordering = ("course", "week_number")
    inlines = [LessonInline, LearningObjectiveInline]


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("module", "title", "lesson_type", "duration_minutes", "order")
    list_filter = ("lesson_type", "module")
    search_fields = ("title", "description")
    inlines = [ResourceInline, LearningObjectiveInline]


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("lesson", "title", "resource_type", "order")
    list_filter = ("resource_type",)
    search_fields = ("title", "description")


@admin.register(models.LearningObjective)
class LearningObjectiveAdmin(admin.ModelAdmin):
    list_display = ("description", "course", "module", "lesson", "order")
    list_filter = ("course", "module")
    search_fields = ("description",)


@admin.register(models.Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "progress_percent", "started_at")
    list_filter = ("status", "course")
    search_fields = ("user__username", "course__title")


@admin.register(models.Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "lesson", "completed", "completed_at", "viewed_at", "quiz_passed")
    list_filter = ("completed",)
    search_fields = ("enrollment__user__username", "lesson__title")


@admin.register(models.CompletionRule)
class CompletionRuleAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "module",
        "require_all_lessons",
        "min_lessons_completed",
        "min_quiz_score",
        "min_progress_percent",
        "require_assignments_approved",
    )
    list_filter = ("require_all_lessons", "require_assignments_approved")


@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "lesson",
        "module",
        "passing_score",
        "is_required_for_completion",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("title",)
    inlines = [QuestionInline]


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "question_type", "points", "order")
    list_filter = ("question_type",)
    inlines = [ChoiceInline]


@admin.register(models.Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "is_correct", "order")
    list_filter = ("is_correct",)


@admin.register(models.Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "enrollment", "attempt_number", "score", "passed")
    list_filter = ("passed",)
    search_fields = ("enrollment__user__username", "quiz__title")
    inlines = [SubmissionAnswerInline]
    actions = ["mark_short_reviewed_and_recompute"]

    def mark_short_reviewed_and_recompute(self, request, queryset):
        for submission in queryset.select_related("quiz"):
            answers = submission.answers.select_related("question")
            short_answers = [
                answer
                for answer in answers
                if answer.question.question_type == models.Question.QuestionType.SHORT
                and answer.question.manual_review_required
            ]
            for answer in short_answers:
                if not answer.manual_scored:
                    answer.manual_scored = True
                    answer.reviewed_at = timezone.now()
                    answer.reviewed_by = request.user
                    answer.save(update_fields=["manual_scored", "reviewed_at", "reviewed_by"])
            compute_score(submission)

    mark_short_reviewed_and_recompute.short_description = (
        "Marquer les réponses courtes comme corrigées et recalculer le score"
    )


@admin.register(models.Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "lesson",
        "module",
        "requires_kpi_evidence",
        "is_final_assessment",
        "due_date",
    )
    list_filter = ("requires_kpi_evidence",)
    search_fields = ("title",)
    inlines = [AssignmentKPIInline]


@admin.register(models.AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "enrollment", "status", "submitted_at", "reviewed_at")
    list_filter = ("status",)
    search_fields = ("enrollment__user__username", "assignment__title")
    inlines = [
        AssignmentKPIEvidenceInline,
        AssignmentAttachmentInline,
        AssignmentLinkInline,
        AssignmentKPIValueInline,
    ]
    actions = ["approve_submissions", "reject_submissions"]

    def approve_submissions(self, request, queryset):
        for submission in queryset:
            if request.user.role not in {"OWNER", "ADMIN", "MANAGER"}:
                continue
            submission.status = models.AssignmentSubmission.Status.APPROVED
            submission.reviewed_at = timezone.now()
            submission.reviewed_by = request.user
            submission.save(update_fields=["status", "reviewed_at", "reviewed_by", "updated_at"])

    def reject_submissions(self, request, queryset):
        for submission in queryset:
            if request.user.role not in {"OWNER", "ADMIN", "MANAGER"}:
                continue
            submission.status = models.AssignmentSubmission.Status.REJECTED
            submission.reviewed_at = timezone.now()
            submission.reviewed_by = request.user
            submission.save(update_fields=["status", "reviewed_at", "reviewed_by", "updated_at"])

    approve_submissions.short_description = "Approuver les soumissions sélectionnées"
    reject_submissions.short_description = "Rejeter les soumissions sélectionnées"


@admin.register(models.AssignmentKPIRequirement)
class AssignmentKPIRequirementAdmin(admin.ModelAdmin):
    list_display = ("assignment", "label", "unit", "min_value", "max_value")
    search_fields = ("label",)


@admin.register(models.AssignmentKPIEvidence)
class AssignmentKPIEvidenceAdmin(admin.ModelAdmin):
    list_display = ("submission", "requirement", "value", "crm_client", "activity")
    search_fields = ("requirement__label",)


@admin.register(models.Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "rule_type", "course", "module", "assignment", "is_active")
    list_filter = ("rule_type", "is_active")
    search_fields = ("name",)


@admin.register(models.BadgeAward)
class BadgeAwardAdmin(admin.ModelAdmin):
    list_display = ("badge", "user", "awarded_at")
    list_filter = ("badge",)
    search_fields = ("user__username", "badge__name")


@admin.register(models.Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_number", "enrollment", "status", "issued_at")
    list_filter = ("status",)
    search_fields = ("certificate_number",)
