from django.contrib import admin

from training.models import (
    TrainingActionPlan,
    TrainingStudyMaterial,
    TrainingStudyMaterialProgress,
    TrainingConceptCard,
    TrainingAnswer,
    TrainingChecklistProgress,
    TrainingChoice,
    TrainingEnrollment,
    TrainingEvaluation,
    TrainingLesson,
    TrainingLessonChecklistItem,
    TrainingLessonResource,
    TrainingProgram,
    TrainingProgress,
    TrainingQuestion,
    TrainingQuiz,
    TrainingQuizAttempt,
    TrainingSector,
    TrainingSubmission,
    TrainingWeek,
)


class TrainingLessonResourceInline(admin.TabularInline):
    model = TrainingLessonResource
    extra = 0


class TrainingLessonChecklistInline(admin.TabularInline):
    model = TrainingLessonChecklistItem
    extra = 0


class TrainingChoiceInline(admin.TabularInline):
    model = TrainingChoice
    extra = 0


class TrainingQuestionInline(admin.StackedInline):
    model = TrainingQuestion
    extra = 0


class TrainingAnswerInline(admin.TabularInline):
    model = TrainingAnswer
    extra = 0
    readonly_fields = ("question", "selected_choice", "answer_text", "is_correct", "points_awarded")


class TrainingStudyMaterialInline(admin.StackedInline):
    model = TrainingStudyMaterial
    extra = 0
    fields = ("title", "support_type", "content_md", "is_mandatory", "recommended_before_quiz")


class TrainingConceptCardInline(admin.StackedInline):
    model = TrainingConceptCard
    extra = 0
    fields = ("term", "definition_md", "floxy_example_md")


@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_weeks", "target_role")
    search_fields = ("title",)


@admin.register(TrainingSector)
class TrainingSectorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(TrainingWeek)
class TrainingWeekAdmin(admin.ModelAdmin):
    list_display = ("program", "week_number", "title")
    ordering = ("program", "week_number")


@admin.register(TrainingLesson)
class TrainingLessonAdmin(admin.ModelAdmin):
    list_display = ("week", "title", "lesson_type", "duration_minutes")
    list_filter = ("lesson_type",)
    search_fields = ("title",)
    inlines = [
        TrainingLessonResourceInline,
        TrainingLessonChecklistInline,
        TrainingStudyMaterialInline,
        TrainingConceptCardInline,
    ]


@admin.register(TrainingQuiz)
class TrainingQuizAdmin(admin.ModelAdmin):
    list_display = ("lesson", "created_at", "updated_at")
    search_fields = ("lesson__title",)
    inlines = [TrainingQuestionInline]


@admin.register(TrainingQuestion)
class TrainingQuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "question_type", "order", "points", "is_active")
    list_filter = ("question_type", "is_active")
    search_fields = ("question_text",)
    inlines = [TrainingChoiceInline]


@admin.register(TrainingChoice)
class TrainingChoiceAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("choice_text",)


@admin.register(TrainingQuizAttempt)
class TrainingQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("quiz", "user", "score_percent", "passed", "started_at", "submitted_at")
    list_filter = ("passed",)
    search_fields = ("user__email", "user__username", "quiz__lesson__title")
    inlines = [TrainingAnswerInline]


@admin.register(TrainingStudyMaterial)
class TrainingStudyMaterialAdmin(admin.ModelAdmin):
    list_display = ("lesson", "title", "support_type", "is_mandatory", "recommended_before_quiz")
    list_filter = ("support_type", "is_mandatory", "recommended_before_quiz")
    search_fields = ("title", "lesson__title")


@admin.register(TrainingStudyMaterialProgress)
class TrainingStudyMaterialProgressAdmin(admin.ModelAdmin):
    list_display = ("material", "user", "viewed_at")
    search_fields = ("material__title", "user__email", "user__username")


@admin.register(TrainingConceptCard)
class TrainingConceptCardAdmin(admin.ModelAdmin):
    list_display = ("lesson", "term")
    search_fields = ("term", "lesson__title")

@admin.register(TrainingAnswer)
class TrainingAnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "is_correct", "points_awarded")
    list_filter = ("is_correct",)
    search_fields = ("attempt__user__email", "question__question_text")


@admin.register(TrainingSubmission)
class TrainingSubmissionAdmin(admin.ModelAdmin):
    list_display = ("lesson", "user", "status", "submitted_at", "score_percent")
    list_filter = ("status",)
    search_fields = ("lesson__title", "user__email", "user__username")


@admin.register(TrainingEnrollment)
class TrainingEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "program", "status", "started_at")
    list_filter = ("status",)


@admin.register(TrainingProgress)
class TrainingProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "lesson", "completed", "completed_at")
    list_filter = ("completed",)


@admin.register(TrainingChecklistProgress)
class TrainingChecklistProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "checklist_item", "is_done", "updated_at")
    list_filter = ("is_done",)


@admin.register(TrainingEvaluation)
class TrainingEvaluationAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "score", "evaluated_at")


@admin.register(TrainingActionPlan)
class TrainingActionPlanAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "title", "status", "due_date")
    list_filter = ("status",)
