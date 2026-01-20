from django.urls import include, path
from rest_framework.routers import DefaultRouter

from lms import views

router = DefaultRouter()
router.register("courses", views.CourseViewSet, basename="lms-course")
router.register("modules", views.CourseModuleViewSet, basename="lms-module")
router.register("lessons", views.LessonViewSet, basename="lms-lesson")
router.register("resources", views.LessonResourceViewSet, basename="lms-resource")
router.register("quizzes", views.QuizViewSet, basename="lms-quiz")
router.register("quiz-questions", views.QuizQuestionViewSet, basename="lms-quiz-question")
router.register("quiz-choices", views.QuizChoiceViewSet, basename="lms-quiz-choice")
router.register("assignments", views.AssignmentViewSet, basename="lms-assignment")
router.register("assignment-submissions", views.AssignmentSubmissionViewSet, basename="lms-assignment-submission")
router.register("enrollments", views.EnrollmentViewSet, basename="lms-enrollment")
router.register("lesson-progress", views.LessonProgressViewSet, basename="lms-lesson-progress")
router.register("badges", views.BadgeViewSet, basename="lms-badge")
router.register("badge-awards", views.BadgeAwardViewSet, basename="lms-badge-award")
router.register("certificates", views.CertificateViewSet, basename="lms-certificate")

urlpatterns = [
    path("certificates/verify/<uuid:certificate_id>/", views.verify_certificate, name="lms-certificate-verify"),
    path("", include(router.urls)),
]
