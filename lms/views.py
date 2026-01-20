from django.core.exceptions import ValidationError
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from crm.models import Client
from lms.models import (
    Assignment,
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
    QuizChoice,
    QuizQuestion,
)
from lms.permissions import IsEnrollmentOwnerOrAdmin, IsLmsAdmin, IsReadOnlyOrAdmin
from lms.serializers import (
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
    AssignmentSubmitSerializer,
    BadgeAwardSerializer,
    BadgeSerializer,
    CertificateSerializer,
    CourseModuleSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    LessonProgressSerializer,
    LessonResourceSerializer,
    LessonSerializer,
    QuizAttemptSerializer,
    QuizChoiceSerializer,
    QuizQuestionSerializer,
    QuizSerializer,
    QuizSubmitSerializer,
)
from lms.services.assignments import review_submission, submit_assignment
from lms.services.badges import award_badges_for_enrollment
from lms.services.certificates import issue_certificate
from lms.services.progress import mark_lesson_viewed, refresh_enrollment_progress
from lms.services.quiz import score_quiz_attempt
from operations.models import Activity


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class CourseModuleViewSet(viewsets.ModelViewSet):
    queryset = CourseModule.objects.select_related("course")
    serializer_class = CourseModuleSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related("module", "module__course")
    serializer_class = LessonSerializer
    permission_classes = [IsReadOnlyOrAdmin]

    @action(detail=True, methods=["post"], permission_classes=[IsEnrollmentOwnerOrAdmin])
    def mark_viewed(self, request, pk=None):
        lesson = self.get_object()
        enrollment_id = request.data.get("enrollment_id")
        if not enrollment_id:
            raise DRFValidationError({"enrollment_id": "L'inscription est obligatoire."})
        enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
        if enrollment.user_id != request.user.id and request.user.role not in {"OWNER", "ADMIN", "MANAGER"}:
            raise DRFValidationError({"detail": "Accès refusé."})
        progress = mark_lesson_viewed(enrollment, lesson)
        refresh_enrollment_progress(enrollment)
        return Response(LessonProgressSerializer(progress).data, status=status.HTTP_200_OK)


class LessonResourceViewSet(viewsets.ModelViewSet):
    queryset = LessonResource.objects.select_related("lesson")
    serializer_class = LessonResourceSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related("lesson", "module")
    serializer_class = QuizSerializer
    permission_classes = [IsReadOnlyOrAdmin]

    @action(detail=True, methods=["post"], permission_classes=[IsEnrollmentOwnerOrAdmin])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = get_object_or_404(Enrollment, pk=serializer.validated_data["enrollment_id"])
        if enrollment.user_id != request.user.id and request.user.role not in {"OWNER", "ADMIN", "MANAGER"}:
            raise DRFValidationError({"detail": "Accès refusé."})
        try:
            attempt = score_quiz_attempt(enrollment, quiz, serializer.validated_data["answers"])
        except ValidationError as exc:
            raise DRFValidationError(exc.message_dict or {"detail": str(exc)}) from exc
        return Response(QuizAttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


class QuizQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuizQuestion.objects.select_related("quiz")
    serializer_class = QuizQuestionSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class QuizChoiceViewSet(viewsets.ModelViewSet):
    queryset = QuizChoice.objects.select_related("question")
    serializer_class = QuizChoiceSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related("lesson", "module")
    serializer_class = AssignmentSerializer
    permission_classes = [IsReadOnlyOrAdmin]

    @action(detail=True, methods=["post"], permission_classes=[IsEnrollmentOwnerOrAdmin])
    def submit(self, request, pk=None):
        assignment = self.get_object()
        serializer = AssignmentSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = get_object_or_404(Enrollment, pk=serializer.validated_data["enrollment_id"])
        if enrollment.user_id != request.user.id and request.user.role not in {"OWNER", "ADMIN", "MANAGER"}:
            raise DRFValidationError({"detail": "Accès refusé."})

        evidence_payloads = []
        for evidence in serializer.validated_data.get("evidence", []):
            requirement = None
            if evidence.get("requirement_id"):
                requirement = get_object_or_404(
                    AssignmentKPIRequirement, pk=evidence["requirement_id"], assignment=assignment
                )
            crm_client = None
            if evidence.get("crm_client_id"):
                crm_client = get_object_or_404(Client, pk=evidence["crm_client_id"])
            activity = None
            if evidence.get("activity_id"):
                activity = get_object_or_404(Activity, pk=evidence["activity_id"])
            evidence_payloads.append(
                {
                    "requirement": requirement,
                    "value": evidence["value"],
                    "proof_url": evidence.get("proof_url", ""),
                    "proof_file": evidence.get("proof_file"),
                    "crm_client": crm_client,
                    "activity": activity,
                }
            )

        try:
            submission = submit_assignment(
                enrollment,
                assignment,
                response_text=serializer.validated_data.get("response_text", ""),
                evidence_payloads=evidence_payloads,
                attachments=serializer.validated_data.get("attachments"),
                proof_links=serializer.validated_data.get("proof_links"),
                kpis=serializer.validated_data.get("kpis"),
            )
        except ValidationError as exc:
            raise DRFValidationError(exc.message_dict or {"detail": str(exc)}) from exc

        return Response(
            AssignmentSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED
        )


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.select_related("assignment", "enrollment")
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsEnrollmentOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in {"OWNER", "ADMIN", "MANAGER"}:
            return self.queryset
        return self.queryset.filter(enrollment__user=user)

    def get_permissions(self):
        if self.request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            return [IsLmsAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], permission_classes=[IsLmsAdmin])
    def approve(self, request, pk=None):
        submission = self.get_object()
        feedback = request.data.get("feedback", "")
        try:
            submission = review_submission(
                submission,
                reviewer=request.user,
                status=AssignmentSubmission.Status.APPROVED,
                feedback=feedback,
            )
        except ValidationError as exc:
            raise DRFValidationError(exc.message_dict or {"detail": str(exc)}) from exc
        return Response(AssignmentSubmissionSerializer(submission).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsLmsAdmin])
    def reject(self, request, pk=None):
        submission = self.get_object()
        feedback = request.data.get("feedback", "")
        try:
            submission = review_submission(
                submission,
                reviewer=request.user,
                status=AssignmentSubmission.Status.REJECTED,
                feedback=feedback,
            )
        except ValidationError as exc:
            raise DRFValidationError(exc.message_dict or {"detail": str(exc)}) from exc
        return Response(AssignmentSubmissionSerializer(submission).data, status=status.HTTP_200_OK)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related("user", "course")
    serializer_class = EnrollmentSerializer
    permission_classes = [IsEnrollmentOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in {"OWNER", "ADMIN", "MANAGER"}:
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role in {"OWNER", "ADMIN", "MANAGER"}:
            serializer.save()
        else:
            serializer.save(user=user)

    @action(detail=True, methods=["post"], permission_classes=[IsEnrollmentOwnerOrAdmin])
    def refresh(self, request, pk=None):
        enrollment = self.get_object()
        refresh_enrollment_progress(enrollment)
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsEnrollmentOwnerOrAdmin])
    def award_badges(self, request, pk=None):
        enrollment = self.get_object()
        awards = award_badges_for_enrollment(enrollment)
        return Response(BadgeAwardSerializer(awards, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsLmsAdmin])
    def issue_certificate(self, request, pk=None):
        enrollment = self.get_object()
        try:
            certificate = issue_certificate(enrollment, created_by=request.user)
        except ValidationError as exc:
            raise DRFValidationError(exc.message_dict or {"detail": str(exc)}) from exc
        return Response(CertificateSerializer(certificate).data, status=status.HTTP_201_CREATED)


class LessonProgressViewSet(viewsets.ModelViewSet):
    queryset = LessonProgress.objects.select_related("enrollment", "lesson")
    serializer_class = LessonProgressSerializer
    permission_classes = [IsEnrollmentOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in {"OWNER", "ADMIN", "MANAGER"}:
            return self.queryset
        return self.queryset.filter(enrollment__user=user)


class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [IsReadOnlyOrAdmin]


class BadgeAwardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BadgeAward.objects.select_related("badge", "user", "enrollment")
    serializer_class = BadgeAwardSerializer
    permission_classes = [IsEnrollmentOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in {"OWNER", "ADMIN", "MANAGER"}:
            return self.queryset
        return self.queryset.filter(user=user)


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certificate.objects.select_related("enrollment", "enrollment__user")
    serializer_class = CertificateSerializer
    permission_classes = [IsEnrollmentOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in {"OWNER", "ADMIN", "MANAGER"}:
            return self.queryset
        return self.queryset.filter(enrollment__user=user)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        certificate = self.get_object()
        if not certificate.pdf_file:
            raise DRFValidationError({"detail": "PDF non disponible."})
        certificate.pdf_file.open("rb")
        return FileResponse(
            certificate.pdf_file,
            as_attachment=True,
            filename=f"certificate-{certificate.certificate_number}.pdf",
            content_type="application/pdf",
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def verify_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    holder_name = certificate.enrollment.user.get_full_name() or certificate.enrollment.user.username
    if request.accepted_renderer.format == "html":
        return render(
            request,
            "lms/certificate_verify.html",
            {"certificate": certificate, "holder_name": holder_name},
        )
    return Response(
        {
            "certificate_number": certificate.certificate_number,
            "status": certificate.status,
            "valid": certificate.status == certificate.Status.ISSUED,
            "issued_at": certificate.issued_at,
            "course": certificate.enrollment.course.title,
            "holder_name": holder_name,
        },
        status=status.HTTP_200_OK,
    )
