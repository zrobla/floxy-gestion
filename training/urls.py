from django.urls import path

from training.views import (
    training_complete_lesson,
    training_evaluation,
    training_home,
    training_lesson_detail,
    training_mark_study_material_viewed,
    training_glossary,
    training_submit_quiz,
    training_program_pdf,
    training_program_detail,
    training_report_pdf,
    training_progress_pdf,
    training_reporting,
    training_toggle_checklist,
)

urlpatterns = [
    path("", training_home, name="training_home"),
    path("glossaire/", training_glossary, name="training_glossary"),
    path("reporting/", training_reporting, name="training_reporting"),
    path("reporting/global.pdf", training_report_pdf, name="training_report_pdf"),
    path("programme/<int:program_id>/", training_program_detail, name="training_program"),
    path(
        "programme/<int:program_id>/plan.pdf",
        training_program_pdf,
        name="training_program_pdf",
    ),
    path("module/<int:lesson_id>/", training_lesson_detail, name="training_lesson"),
    path(
        "module/<int:lesson_id>/support/<int:material_id>/viewed/",
        training_mark_study_material_viewed,
        name="training_support_viewed",
    ),
    path("module/<int:lesson_id>/quiz/", training_submit_quiz, name="training_quiz_submit"),
    path("module/<int:lesson_id>/terminer/", training_complete_lesson, name="training_complete"),
    path(
        "module/<int:lesson_id>/checklist/<int:item_id>/toggle/",
        training_toggle_checklist,
        name="training_checklist_toggle",
    ),
    path(
        "reporting/enrollment/<int:enrollment_id>/progress.pdf",
        training_progress_pdf,
        name="training_progress_pdf",
    ),
    path("programme/<int:program_id>/evaluation/", training_evaluation, name="training_evaluation"),
]
