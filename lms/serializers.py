from django.contrib.auth import get_user_model
from rest_framework import serializers

from lms.models import (
    Assignment,
    AssignmentKPIEvidence,
    AssignmentKPIRequirement,
    AssignmentSubmission,
    Badge,
    BadgeAward,
    Certificate,
    Course,
    CourseModule,
    Enrollment,
    Lesson,
    LessonProgress,
    LessonResource,
    Quiz,
    QuizAnswer,
    QuizAttempt,
    QuizChoice,
    QuizQuestion,
)

User = get_user_model()


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "objectives",
            "duration_weeks",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = (
            "id",
            "course",
            "week_number",
            "title",
            "objective",
            "overview",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class LessonResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonResource
        fields = (
            "id",
            "lesson",
            "title",
            "description",
            "resource_type",
            "url",
            "file",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class LessonSerializer(serializers.ModelSerializer):
    resources = LessonResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "module",
            "title",
            "description",
            "content",
            "lesson_type",
            "duration_minutes",
            "order",
            "is_required",
            "created_at",
            "updated_at",
            "resources",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class QuizChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizChoice
        fields = ("id", "question", "text", "is_correct", "order")
        read_only_fields = ("id",)


class QuizQuestionSerializer(serializers.ModelSerializer):
    choices = QuizChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = QuizQuestion
        fields = (
            "id",
            "quiz",
            "question_type",
            "prompt",
            "points",
            "order",
            "correct_text",
            "case_sensitive",
            "manual_review_required",
            "choices",
        )
        read_only_fields = ("id",)


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = (
            "id",
            "lesson",
            "module",
            "title",
            "description",
            "passing_score",
            "max_attempts",
            "is_required_for_completion",
            "is_active",
            "created_at",
            "updated_at",
            "questions",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = (
            "id",
            "attempt",
            "question",
            "selected_choice",
            "text_answer",
            "is_correct",
            "score_awarded",
        )
        read_only_fields = ("id", "is_correct", "score_awarded")


class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = (
            "id",
            "enrollment",
            "quiz",
            "attempt_number",
            "submitted_at",
            "score",
            "max_score",
            "passed",
            "answers",
        )
        read_only_fields = ("id", "attempt_number", "submitted_at", "score", "max_score", "passed")


class QuizSubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField(required=False)
    text_answer = serializers.CharField(required=False, allow_blank=True)


class QuizSubmitSerializer(serializers.Serializer):
    enrollment_id = serializers.IntegerField()
    answers = QuizSubmitAnswerSerializer(many=True)


class AssignmentKPIRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentKPIRequirement
        fields = (
            "id",
            "assignment",
            "label",
            "unit",
            "min_value",
            "max_value",
            "is_required",
            "order",
        )
        read_only_fields = ("id",)


class AssignmentSerializer(serializers.ModelSerializer):
    kpi_requirements = AssignmentKPIRequirementSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = (
            "id",
            "lesson",
            "module",
            "title",
            "description",
            "instructions",
            "due_date",
            "requires_kpi_evidence",
            "max_score",
            "requires_review",
            "is_final_assessment",
            "created_at",
            "updated_at",
            "kpi_requirements",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AssignmentKPIEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentKPIEvidence
        fields = (
            "id",
            "submission",
            "requirement",
            "value",
            "proof_url",
            "proof_file",
            "notes",
            "crm_client",
            "activity",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField()
    proof_links = serializers.SerializerMethodField()
    kpi_values = serializers.SerializerMethodField()
    kpi_evidence = AssignmentKPIEvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = (
            "id",
            "enrollment",
            "assignment",
            "response_text",
            "status",
            "score",
            "feedback",
            "submitted_at",
            "reviewed_at",
            "reviewed_by",
            "kpi_evidence",
            "attachments",
            "proof_links",
            "kpi_values",
        )
        read_only_fields = ("id", "submitted_at", "reviewed_at", "reviewed_by")

    def get_attachments(self, obj):
        return [
            {"id": attachment.id, "image": attachment.image.url, "caption": attachment.caption}
            for attachment in obj.attachments.all()
        ]

    def get_proof_links(self, obj):
        return [
            {"id": link.id, "url": link.url, "label": link.label}
            for link in obj.proof_links.all()
        ]

    def get_kpi_values(self, obj):
        return [
            {"id": kpi.id, "label": kpi.label, "value": kpi.value, "unit": kpi.unit}
            for kpi in obj.kpi_values.all()
        ]


class AssignmentSubmitEvidenceSerializer(serializers.Serializer):
    requirement_id = serializers.IntegerField(required=False)
    value = serializers.DecimalField(max_digits=10, decimal_places=2)
    proof_url = serializers.URLField(required=False, allow_blank=True)
    proof_file = serializers.FileField(required=False, allow_null=True)
    crm_client_id = serializers.IntegerField(required=False)
    activity_id = serializers.IntegerField(required=False)


class AssignmentSubmitKPISerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.DecimalField(max_digits=10, decimal_places=2)
    unit = serializers.CharField(required=False, allow_blank=True)


class AssignmentSubmitSerializer(serializers.Serializer):
    enrollment_id = serializers.IntegerField()
    response_text = serializers.CharField(required=False, allow_blank=True)
    evidence = AssignmentSubmitEvidenceSerializer(many=True, required=False)
    attachments = serializers.ListField(
        child=serializers.ImageField(), required=False, allow_empty=True
    )
    proof_links = serializers.ListField(
        child=serializers.URLField(), required=False, allow_empty=True
    )
    kpis = AssignmentSubmitKPISerializer(many=True, required=False)


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = (
            "id",
            "user",
            "course",
            "status",
            "progress_percent",
            "started_at",
            "completed_at",
            "updated_at",
        )
        read_only_fields = ("id", "progress_percent", "started_at", "completed_at", "updated_at")


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = (
            "id",
            "enrollment",
            "lesson",
            "completed",
            "completed_at",
            "viewed_at",
            "quiz_passed",
            "notes",
        )
        read_only_fields = ("id",)


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = (
            "id",
            "name",
            "description",
            "icon",
            "rule_type",
            "course",
            "module",
            "assignment",
            "min_score",
            "kpi_label",
            "kpi_min_value",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class BadgeAwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BadgeAward
        fields = ("id", "badge", "user", "enrollment", "awarded_at", "notes")
        read_only_fields = ("id", "awarded_at")


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = (
            "id",
            "enrollment",
            "certificate_number",
            "issued_at",
            "status",
            "pdf_file",
            "created_by",
        )
        read_only_fields = ("id", "certificate_number", "issued_at", "pdf_file")
