from io import BytesIO
import textwrap

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

try:
    import markdown as md
except ImportError:  # pragma: no cover - optional dependency
    md = None
from training.forms import TrainingActionPlanForm, TrainingEvaluationForm
from training.models import (
    TrainingActionPlan,
    TrainingChecklistProgress,
    TrainingEnrollment,
    TrainingEvaluation,
    TrainingLesson,
    TrainingLessonChecklistItem,
    TrainingProgram,
    TrainingProgress,
    TrainingQuestion,
    TrainingQuiz,
    TrainingQuizAttempt,
    TrainingAnswer,
    TrainingStudyMaterial,
    TrainingStudyMaterialProgress,
    TrainingConceptCard,
)
from training.utils import lesson_completion_status


@login_required
def training_home(request):
    program = TrainingProgram.objects.prefetch_related("weeks", "sectors").first()
    enrollment = None
    progress_percent = 0
    total_lessons = 0
    completed_lessons = 0
    remaining_lessons = 0
    quiz_passed_count = 0

    if program:
        enrollment = TrainingEnrollment.objects.filter(
            program=program, user=request.user
        ).first()
        if enrollment:
            progress_percent = enrollment.get_progress_percent()
            total_lessons = TrainingLesson.objects.filter(week__program=program).count()
            completed_lessons = TrainingProgress.objects.filter(
                enrollment=enrollment, completed=True
            ).count()
            remaining_lessons = max(total_lessons - completed_lessons, 0)
            quiz_passed_count = TrainingProgress.objects.filter(
                enrollment=enrollment, quiz_passed=True
            ).count()

    if request.method == "POST" and program:
        if "start_training" in request.POST:
            enrollment, created = TrainingEnrollment.objects.get_or_create(
                program=program, user=request.user
            )
            if created:
                messages.success(request, "Formation démarrée.")
            return redirect("training_home")

    return render(
        request,
        "training/home.html",
        {
            "titre": "Formation",
            "page_theme": "training",
            "program": program,
            "enrollment": enrollment,
            "progress_percent": progress_percent,
            "can_manage": _role_in(request.user, {"OWNER", "ADMIN", "MANAGER"}),
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "remaining_lessons": remaining_lessons,
            "quiz_passed_count": quiz_passed_count,
        },
    )


@login_required
def training_glossary(request):
    query = request.GET.get("q", "").strip()
    cards = TrainingConceptCard.objects.select_related("lesson", "lesson__week").order_by(
        "term"
    )
    if query:
        cards = cards.filter(
            Q(term__icontains=query)
            | Q(definition_md__icontains=query)
            | Q(floxy_example_md__icontains=query)
            | Q(lesson__title__icontains=query)
        )

    glossary_cards = list(cards)
    for card in glossary_cards:
        card.rendered_definition = _render_markdown_minimal(card.definition_md)
        card.rendered_example = _render_markdown_minimal(card.floxy_example_md)

    return render(
        request,
        "training/glossary.html",
        {
            "titre": "Glossaire formation",
            "page_theme": "training",
            "query": query,
            "cards": glossary_cards,
            "result_count": len(glossary_cards),
        },
    )


def _role_in(user, roles) -> bool:
    return bool(user and user.is_authenticated and user.role in roles)


def _render_markdown_minimal(content: str) -> str:
    if not content:
        return ""
    if md:
        return mark_safe(md.markdown(content, extensions=["extra", "sane_lists"]))
    escaped = escape(content)
    return mark_safe(escaped.replace("\n", "<br>"))


def _draw_wrapped_text(pdf, text: str, x: float, y: float, width: int) -> float:
    for line in textwrap.wrap(text, width=width):
        pdf.drawString(x, y, line)
        y -= 14
    return y


def _ensure_space(pdf, y: float, height: float, margin: float) -> float:
    if y < margin:
        pdf.showPage()
        pdf.setFont("Helvetica", 11)
        return height - margin
    return y


@login_required
def training_program_detail(request, program_id):
    program = get_object_or_404(
        TrainingProgram.objects.prefetch_related(
            "sectors",
            "weeks__lessons__sectors",
            "weeks__lessons__resources",
            "weeks__lessons__checklist_items",
        ),
        pk=program_id,
    )
    enrollment, _ = TrainingEnrollment.objects.get_or_create(
        program=program, user=request.user
    )
    progress_items = TrainingProgress.objects.filter(enrollment=enrollment)
    progress_map = {progress.lesson_id: progress for progress in progress_items}
    completed_lessons = {
        progress.lesson_id for progress in progress_items if progress.completed
    }
    total_lessons = TrainingLesson.objects.filter(week__program=program).count()
    completed_lessons_count = len(completed_lessons)
    remaining_lessons = max(total_lessons - completed_lessons_count, 0)
    quiz_passed_count = progress_items.filter(quiz_passed=True).count()

    checklist_progress = TrainingChecklistProgress.objects.filter(enrollment=enrollment)
    checklist_done_ids = {
        progress.checklist_item_id
        for progress in checklist_progress
        if progress.is_done
    }
    checklist_summary = {}
    checklist_items = TrainingLessonChecklistItem.objects.filter(
        lesson__week__program=program
    )
    for item in checklist_items:
        summary = checklist_summary.setdefault(item.lesson_id, {"done": 0, "total": 0})
        summary["total"] += 1
        if item.id in checklist_done_ids:
            summary["done"] += 1

    action_plans = TrainingActionPlan.objects.filter(enrollment=enrollment)
    action_form = TrainingActionPlanForm()
    evaluation = TrainingEvaluation.objects.filter(enrollment=enrollment).first()
    concept_cards = (
        TrainingConceptCard.objects.filter(lesson__week__program=program)
        .select_related("lesson")
        .order_by("term")
    )
    mini_glossary = list(concept_cards[:12])
    for card in mini_glossary:
        card.rendered_definition = _render_markdown_minimal(card.definition_md)
        card.rendered_example = _render_markdown_minimal(card.floxy_example_md)

    for week in program.weeks.all():
        for lesson in week.lessons.all():
            summary = checklist_summary.get(lesson.id, {"done": 0, "total": 0})
            lesson.checklist_done = summary["done"]
            lesson.checklist_total = summary["total"]
            lesson.is_completed = lesson.id in completed_lessons

    if request.method == "POST":
        if "create_action_plan" in request.POST:
            action_form = TrainingActionPlanForm(request.POST)
            if action_form.is_valid():
                action_plan = action_form.save(commit=False)
                action_plan.enrollment = enrollment
                action_plan.save()
                messages.success(request, "Plan d'action ajouté.")
                return redirect("training_program", program_id=program.id)
            messages.error(request, "Veuillez corriger le plan d'action.")
        elif "update_action_plan" in request.POST:
            action_plan_id = request.POST.get("action_plan_id")
            status = request.POST.get("status")
            action_plan = action_plans.filter(pk=action_plan_id).first()
            if action_plan and status in TrainingActionPlan.Status.values:
                action_plan.status = status
                action_plan.save(update_fields=["status", "updated_at"])
                messages.success(request, "Plan d'action mis à jour.")
                return redirect("training_program", program_id=program.id)
            messages.error(request, "Impossible de mettre à jour ce plan.")

    return render(
        request,
        "training/program_detail.html",
        {
            "titre": program.title,
            "page_theme": "training",
            "program": program,
            "enrollment": enrollment,
            "progress_map": progress_map,
            "completed_lessons": completed_lessons,
            "checklist_summary": checklist_summary,
            "progress_percent": enrollment.get_progress_percent(),
            "action_plans": action_plans,
            "action_form": action_form,
            "evaluation": evaluation,
            "action_status_choices": TrainingActionPlan.Status.choices,
            "mini_glossary": mini_glossary,
            "has_more_glossary": concept_cards.count() > len(mini_glossary),
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons_count,
            "remaining_lessons": remaining_lessons,
            "quiz_passed_count": quiz_passed_count,
        },
    )


@login_required
def training_reporting(request):
    program = TrainingProgram.objects.prefetch_related("weeks").first()
    if not program:
        return render(
            request,
            "training/reporting.html",
            {
                "titre": "Reporting formation",
                "page_theme": "training",
                "program": None,
            },
        )

    can_manage = _role_in(request.user, {"OWNER", "ADMIN", "MANAGER"})
    enrollments_qs = TrainingEnrollment.objects.filter(program=program).select_related(
        "user"
    )
    if not can_manage:
        enrollments_qs = enrollments_qs.filter(user=request.user)

    total_lessons = TrainingLesson.objects.filter(week__program=program).count()
    enrollments = list(
        enrollments_qs.annotate(
            completed_lessons=Count(
                "progress_items",
                filter=Q(progress_items__completed=True),
                distinct=True,
            )
        )
    )

    evaluation_qs = TrainingEvaluation.objects.filter(enrollment__in=enrollments)
    evaluation_map = {evaluation.enrollment_id: evaluation for evaluation in evaluation_qs}
    evaluation_avg = (
        round(float(evaluation_qs.aggregate(avg=Avg("score"))["avg"]), 2)
        if evaluation_qs.exists()
        else 0.0
    )

    action_plans = TrainingActionPlan.objects.filter(enrollment__in=enrollments)
    action_plan_summary = {
        status: 0 for status in TrainingActionPlan.Status.values
    }
    for item in action_plans.values("status").annotate(count=Count("id")):
        action_plan_summary[item["status"]] = item["count"]

    action_plan_counts = {
        item["enrollment_id"]: item
        for item in action_plans.values("enrollment_id").annotate(
            total=Count("id"),
            done=Count("id", filter=Q(status=TrainingActionPlan.Status.DONE)),
        )
    }

    progress_percentages = []
    for enrollment in enrollments:
        enrollment.progress_percent = (
            round((enrollment.completed_lessons / total_lessons) * 100, 0)
            if total_lessons
            else 0
        )
        enrollment.evaluation = evaluation_map.get(enrollment.id)
        plan_counts = action_plan_counts.get(enrollment.id, {"total": 0, "done": 0})
        enrollment.action_plan_total = plan_counts["total"]
        enrollment.action_plan_done = plan_counts["done"]
        progress_percentages.append(enrollment.progress_percent)

    progress_avg = (
        round(sum(progress_percentages) / len(progress_percentages), 1)
        if progress_percentages
        else 0
    )
    completed_count = len(
        [enrollment for enrollment in enrollments if enrollment.status == "COMPLETED"]
    )

    return render(
        request,
        "training/reporting.html",
        {
            "titre": "Reporting formation",
            "page_theme": "training",
            "program": program,
            "enrollments": enrollments,
            "total_enrollments": len(enrollments),
            "completed_enrollments": completed_count,
            "progress_avg": progress_avg,
            "evaluation_avg": evaluation_avg,
            "action_plan_summary": action_plan_summary,
            "can_manage": can_manage,
        },
    )


@login_required
def training_report_pdf(request):
    if not _role_in(request.user, {"OWNER", "ADMIN", "MANAGER"}):
        return HttpResponseForbidden("Accès refusé")

    program = TrainingProgram.objects.prefetch_related("weeks").first()
    if not program:
        return HttpResponse("Programme non configuré.", status=404)

    enrollments_qs = TrainingEnrollment.objects.filter(program=program).select_related(
        "user"
    )
    total_lessons = TrainingLesson.objects.filter(week__program=program).count()
    enrollments = list(
        enrollments_qs.annotate(
            completed_lessons=Count(
                "progress_items",
                filter=Q(progress_items__completed=True),
                distinct=True,
            )
        )
    )
    evaluation_qs = TrainingEvaluation.objects.filter(enrollment__in=enrollments)
    evaluation_map = {evaluation.enrollment_id: evaluation for evaluation in evaluation_qs}
    evaluation_avg = (
        round(float(evaluation_qs.aggregate(avg=Avg("score"))["avg"]), 2)
        if evaluation_qs.exists()
        else 0.0
    )

    action_plans = TrainingActionPlan.objects.filter(enrollment__in=enrollments)
    action_plan_summary = {
        status: 0 for status in TrainingActionPlan.Status.values
    }
    for item in action_plans.values("status").annotate(count=Count("id")):
        action_plan_summary[item["status"]] = item["count"]

    action_plan_counts = {
        item["enrollment_id"]: item
        for item in action_plans.values("enrollment_id").annotate(
            total=Count("id"),
            done=Count("id", filter=Q(status=TrainingActionPlan.Status.DONE)),
        )
    }

    progress_percentages = []
    for enrollment in enrollments:
        enrollment.progress_percent = (
            round((enrollment.completed_lessons / total_lessons) * 100, 0)
            if total_lessons
            else 0
        )
        enrollment.evaluation = evaluation_map.get(enrollment.id)
        plan_counts = action_plan_counts.get(enrollment.id, {"total": 0, "done": 0})
        enrollment.action_plan_total = plan_counts["total"]
        enrollment.action_plan_done = plan_counts["done"]
        progress_percentages.append(enrollment.progress_percent)

    progress_avg = (
        round(sum(progress_percentages) / len(progress_percentages), 1)
        if progress_percentages
        else 0
    )
    completed_count = len(
        [enrollment for enrollment in enrollments if enrollment.status == "COMPLETED"]
    )
    generated_at = timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(margin, y, "Rapport global formation")
    y -= 22
    pdf.setFont("Helvetica", 11)
    pdf.drawString(margin, y, f"Programme : {program.title}")
    y -= 16
    pdf.drawString(margin, y, f"Généré le : {generated_at}")
    y -= 16
    y = _draw_wrapped_text(pdf, f"Objectif : {program.objective}", margin, y, 95)
    y -= 10

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y, "Synthèse")
    y -= 16
    pdf.setFont("Helvetica", 11)
    pdf.drawString(margin, y, f"Participants : {len(enrollments)}")
    y -= 14
    pdf.drawString(margin, y, f"Formations terminées : {completed_count}")
    y -= 14
    pdf.drawString(margin, y, f"Progression moyenne : {progress_avg}%")
    y -= 14
    pdf.drawString(margin, y, f"Score moyen d'évaluation : {evaluation_avg}")
    y -= 14
    pdf.drawString(
        margin,
        y,
        "Plans d'action (P/E/R) : "
        f"{action_plan_summary['PLANNED']}/"
        f"{action_plan_summary['IN_PROGRESS']}/"
        f"{action_plan_summary['DONE']}",
    )
    y -= 20

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y, "Progression par participant")
    y -= 18
    pdf.setFont("Helvetica", 10)

    for enrollment in enrollments:
        y = _ensure_space(pdf, y, height, margin)
        status_label = enrollment.get_status_display()
        line = (
            f"• {enrollment.user} | {status_label} | "
            f"{enrollment.progress_percent}%"
        )
        y = _draw_wrapped_text(pdf, line, margin, y, 100)
        if enrollment.evaluation:
            y = _draw_wrapped_text(
                pdf,
                f"  Évaluation : {enrollment.evaluation.score}/100",
                margin + 10,
                y,
                100,
            )
        else:
            y = _draw_wrapped_text(pdf, "  Évaluation : non renseignée", margin + 10, y, 100)
        y = _draw_wrapped_text(
            pdf,
            f"  Plan d'action : {enrollment.action_plan_done}/{enrollment.action_plan_total}",
            margin + 10,
            y,
            100,
        )
        y -= 6

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=reporting-formation.pdf"
    return response


@login_required
def training_program_pdf(request, program_id):
    program = get_object_or_404(
        TrainingProgram.objects.prefetch_related(
            "weeks__lessons__resources", "weeks__lessons__checklist_items"
        ),
        pk=program_id,
    )

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(margin, y, program.title)
    y -= 24
    pdf.setFont("Helvetica", 11)
    y = _draw_wrapped_text(pdf, f"Objectif : {program.objective}", margin, y, 95)
    y -= 10

    for week in program.weeks.all():
        y = _ensure_space(pdf, y, height, margin)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(margin, y, f"Semaine {week.week_number} - {week.title}")
        y -= 18
        pdf.setFont("Helvetica", 11)
        y = _draw_wrapped_text(pdf, f"Objectif : {week.objective}", margin, y, 95)
        if week.focus:
            y = _draw_wrapped_text(pdf, f"Focus : {week.focus}", margin, y, 95)
        y -= 8
        for lesson in week.lessons.all():
            y = _ensure_space(pdf, y, height, margin)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(
                margin,
                y,
                f"• {lesson.title} ({lesson.get_lesson_type_display()})",
            )
            y -= 14
            pdf.setFont("Helvetica", 10)
            if lesson.objective:
                y = _draw_wrapped_text(pdf, f"Objectif : {lesson.objective}", margin + 14, y, 90)
            if lesson.key_points:
                y = _draw_wrapped_text(pdf, f"Points clés : {lesson.key_points}", margin + 14, y, 90)
            if lesson.deliverables:
                y = _draw_wrapped_text(
                    pdf, f"Livrables : {lesson.deliverables}", margin + 14, y, 90
                )
            if lesson.checklist_items.exists():
                y = _draw_wrapped_text(
                    pdf,
                    "Checklist : " + ", ".join(
                        item.label for item in lesson.checklist_items.all()
                    ),
                    margin + 14,
                    y,
                    90,
                )
            y -= 6

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=plan-formation.pdf"
    return response


@login_required
def training_progress_pdf(request, enrollment_id):
    enrollment = get_object_or_404(
        TrainingEnrollment.objects.select_related("user", "program"),
        pk=enrollment_id,
    )
    if not _role_in(request.user, {"OWNER", "ADMIN", "MANAGER"}) and enrollment.user_id != request.user.id:
        return HttpResponseForbidden("Accès refusé")

    program = TrainingProgram.objects.prefetch_related(
        "weeks__lessons__checklist_items"
    ).get(pk=enrollment.program_id)
    total_lessons = TrainingLesson.objects.filter(week__program=program).count()
    completed_lessons = set(
        TrainingProgress.objects.filter(enrollment=enrollment, completed=True).values_list(
            "lesson_id", flat=True
        )
    )
    checklist_done = set(
        TrainingChecklistProgress.objects.filter(
            enrollment=enrollment, is_done=True
        ).values_list("checklist_item_id", flat=True)
    )
    evaluation = TrainingEvaluation.objects.filter(enrollment=enrollment).first()
    action_plans = TrainingActionPlan.objects.filter(enrollment=enrollment)

    progress_percent = (
        round((len(completed_lessons) / total_lessons) * 100, 0) if total_lessons else 0
    )

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(margin, y, "Rapport de progression")
    y -= 24
    pdf.setFont("Helvetica", 11)
    pdf.drawString(margin, y, f"Participant : {enrollment.user}")
    y -= 16
    pdf.drawString(margin, y, f"Programme : {program.title}")
    y -= 16
    pdf.drawString(margin, y, f"Progression : {progress_percent}%")
    y -= 16
    if evaluation:
        pdf.drawString(
            margin,
            y,
            f"Évaluation finale : {evaluation.score}/100 ({'Validée' if evaluation.is_passed else 'À renforcer'})",
        )
        y -= 16
    y -= 6

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y, "Modules et checklists")
    y -= 18
    pdf.setFont("Helvetica", 10)
    for week in program.weeks.all():
        y = _ensure_space(pdf, y, height, margin)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(margin, y, f"Semaine {week.week_number} - {week.title}")
        y -= 14
        pdf.setFont("Helvetica", 10)
        for lesson in week.lessons.all():
            status = "Terminé" if lesson.id in completed_lessons else "En cours"
            checklist_total = lesson.checklist_items.count()
            checklist_done_count = len(
                [item for item in lesson.checklist_items.all() if item.id in checklist_done]
            )
            line = (
                f"• {lesson.title} - {status}"
                f" (Checklist {checklist_done_count}/{checklist_total})"
                if checklist_total
                else f"• {lesson.title} - {status}"
            )
            y = _draw_wrapped_text(pdf, line, margin + 10, y, 90)
        y -= 6

    y = _ensure_space(pdf, y, height, margin)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y, "Plan d'actions 90 jours")
    y -= 16
    pdf.setFont("Helvetica", 10)
    if action_plans.exists():
        for plan in action_plans:
            y = _ensure_space(pdf, y, height, margin)
            plan_line = f"• {plan.title} ({plan.get_status_display()})"
            y = _draw_wrapped_text(pdf, plan_line, margin + 10, y, 90)
            if plan.description:
                y = _draw_wrapped_text(pdf, plan.description, margin + 20, y, 90)
            y -= 4
    else:
        pdf.drawString(margin + 10, y, "Aucun plan d'action enregistré.")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=progression-formation.pdf"
    return response


@login_required
def training_lesson_detail(request, lesson_id):
    lesson = get_object_or_404(
        TrainingLesson.objects.select_related("week__program").prefetch_related(
            "resources", "checklist_items", "sectors", "study_materials", "concept_cards"
        ),
        pk=lesson_id,
    )
    enrollment = TrainingEnrollment.objects.filter(
        program=lesson.week.program, user=request.user
    ).first()
    if not enrollment:
        messages.error(request, "Veuillez démarrer la formation d'abord.")
        return redirect("training_home")

    progress = TrainingProgress.objects.filter(
        enrollment=enrollment, lesson=lesson
    ).first()
    checklist_progress = {
        progress.checklist_item_id: progress
        for progress in TrainingChecklistProgress.objects.filter(enrollment=enrollment)
    }
    for item in lesson.checklist_items.all():
        progress_item = checklist_progress.get(item.id)
        item.is_done = bool(progress_item and progress_item.is_done)
    for resource in lesson.resources.all():
        base_resource_content = resource.content_md or resource.description or ""
        resource.rendered_content = _render_markdown_minimal(base_resource_content)
    study_materials = list(lesson.study_materials.all())
    study_progress_ids = set(
        TrainingStudyMaterialProgress.objects.filter(
            user=request.user, material__lesson=lesson
        ).values_list("material_id", flat=True)
    )
    missing_mandatory_supports = []
    for material in study_materials:
        material.rendered_content = _render_markdown_minimal(material.content_md)
        material.is_viewed = material.id in study_progress_ids
        if material.is_mandatory and not material.is_viewed:
            missing_mandatory_supports.append(material)
    concept_cards = list(lesson.concept_cards.all())
    for card in concept_cards:
        card.rendered_definition = _render_markdown_minimal(card.definition_md)
        card.rendered_example = _render_markdown_minimal(card.floxy_example_md)
    can_access_quiz = _role_in(request.user, {"OWNER", "ADMIN", "MANAGER"})
    quiz = None
    quiz_exists = False
    if can_access_quiz:
        quiz = (
            TrainingQuiz.objects.filter(lesson=lesson)
            .prefetch_related("questions__choices")
            .first()
        )
        quiz_exists = bool(quiz)
    else:
        quiz_exists = TrainingQuiz.objects.filter(lesson=lesson).exists()
    last_attempt = None
    best_score = None
    active_questions = []
    if quiz:
        attempts = TrainingQuizAttempt.objects.filter(
            quiz=quiz, user=request.user
        ).order_by("-submitted_at", "-started_at")
        last_attempt = (
            attempts.filter(
                submitted_at__isnull=False,
                answers__question__is_active=True,
            )
            .distinct()
            .first()
        )
        if progress and progress.quiz_best_score is not None:
            best_score = progress.quiz_best_score
        else:
            scored = [
                attempt.score_percent
                for attempt in attempts
                if attempt.score_percent is not None
            ]
            best_score = max(scored) if scored else None
        last_answers = {}
        if last_attempt:
            last_answers = {
                answer.question_id: answer
                for answer in last_attempt.answers.select_related("selected_choice")
            }
        active_questions = list(quiz.questions.filter(is_active=True))
        for question in active_questions:
            question.last_answer = last_answers.get(question.id)
    required_remaining = TrainingLessonChecklistItem.objects.filter(
        lesson=lesson, is_required=True
    ).exclude(id__in=[item.id for item in lesson.checklist_items.all() if item.is_done])
    base_content = lesson.content_md or lesson.description or ""
    rendered_content = _render_markdown_minimal(base_content)
    completion_status = lesson_completion_status(request.user, lesson)
    sections = [
        {"id": "lessonContent", "label": "Contenu"},
        {"id": "lessonSupports", "label": "Supports d’étude"},
        {"id": "lessonStatus", "label": "Statut"},
    ]
    if concept_cards:
        sections.append({"id": "lessonLexique", "label": "Lexique"})
    sections.extend(
        [
            {"id": "lessonResources", "label": "Ressources"},
            {"id": "lessonChecklist", "label": "Checklist"},
        ]
    )
    if quiz_exists:
        sections.append({"id": "lessonQuiz", "label": "Quiz"})

    return render(
        request,
        "training/lesson_detail.html",
        {
            "titre": lesson.title,
            "page_theme": "training",
            "lesson": lesson,
            "program": lesson.week.program,
            "enrollment": enrollment,
            "progress": progress,
            "checklist_progress": checklist_progress,
            "required_remaining": required_remaining.exists(),
            "rendered_content": rendered_content,
            "video_url": lesson.video_url,
            "quiz": quiz,
            "active_questions": active_questions,
            "last_attempt": last_attempt,
            "best_score": best_score,
            "can_access_quiz": can_access_quiz,
            "quiz_exists": quiz_exists,
            "completion_status": completion_status,
            "study_materials": study_materials,
            "missing_mandatory_supports": missing_mandatory_supports,
            "concept_cards": concept_cards,
            "sections": sections,
        },
    )


@login_required
def training_submit_quiz(request, lesson_id):
    if request.method != "POST":
        return redirect("training_lesson", lesson_id=lesson_id)

    lesson = get_object_or_404(TrainingLesson, pk=lesson_id)
    if not _role_in(request.user, {"OWNER", "ADMIN", "MANAGER"}):
        return HttpResponseForbidden("Accès refusé")

    quiz = (
        TrainingQuiz.objects.filter(lesson=lesson)
        .prefetch_related("questions__choices")
        .first()
    )
    if not quiz:
        messages.error(request, "Aucun quiz disponible pour ce module.")
        return redirect("training_lesson", lesson_id=lesson_id)

    with transaction.atomic():
        attempt = TrainingQuizAttempt.objects.create(
            quiz=quiz, user=request.user, submitted_at=timezone.now()
        )
        total_points = 0
        earned_points = 0

        for question in quiz.questions.filter(is_active=True):
            field_name = f"question_{question.id}"
            raw_value = request.POST.get(field_name, "").strip()
            selected_choice = None
            answer_text = ""
            is_correct = None
            points_awarded = 0

            if question.question_type == TrainingQuestion.QuestionType.OPEN:
                answer_text = raw_value
            else:
                total_points += question.points
                if raw_value:
                    selected_choice = question.choices.filter(id=raw_value).first()
                    if selected_choice:
                        is_correct = selected_choice.is_correct
                        if is_correct:
                            points_awarded = question.points
                    else:
                        is_correct = False
                else:
                    is_correct = False

            earned_points += points_awarded
            TrainingAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=selected_choice,
                answer_text=answer_text,
                is_correct=is_correct,
                points_awarded=points_awarded,
            )

        score_percent = (
            round((earned_points / total_points) * 100) if total_points else 0
        )
        passed = score_percent >= lesson.passing_score
        attempt.score_percent = score_percent
        attempt.passed = passed
        attempt.save(update_fields=["score_percent", "passed"])

        if enrollment:
            progress, _ = TrainingProgress.objects.get_or_create(
                enrollment=enrollment, lesson=lesson
            )
            current_best = (
                progress.quiz_best_score
                if progress.quiz_best_score is not None
                else -1
            )
            if score_percent > current_best:
                progress.quiz_best_score = score_percent
            if passed:
                progress.quiz_passed = True
            progress.save(update_fields=["quiz_best_score", "quiz_passed"])

    messages.success(request, f"Quiz soumis. Score: {score_percent}%.")
    return redirect("training_lesson", lesson_id=lesson_id)


@login_required
def training_mark_study_material_viewed(request, lesson_id, material_id):
    if request.method != "POST":
        return redirect("training_lesson", lesson_id=lesson_id)

    material = get_object_or_404(
        TrainingStudyMaterial.objects.select_related("lesson__week__program"),
        pk=material_id,
        lesson_id=lesson_id,
    )
    enrollment = TrainingEnrollment.objects.filter(
        program=material.lesson.week.program, user=request.user
    ).first()
    if not enrollment and not _role_in(request.user, {"OWNER", "ADMIN", "MANAGER"}):
        return HttpResponseForbidden("Accès refusé")

    TrainingStudyMaterialProgress.objects.get_or_create(
        material=material, user=request.user
    )
    messages.success(request, "Support marqué comme consulté.")
    return redirect("training_lesson", lesson_id=lesson_id)


@login_required
def training_toggle_checklist(request, lesson_id, item_id):
    if request.method != "POST":
        return redirect("training_lesson", lesson_id=lesson_id)

    lesson = get_object_or_404(TrainingLesson, pk=lesson_id)
    enrollment = TrainingEnrollment.objects.filter(
        program=lesson.week.program, user=request.user
    ).first()
    if not enrollment:
        messages.error(request, "Veuillez démarrer la formation d'abord.")
        return redirect("training_home")

    checklist_item = get_object_or_404(
        TrainingLessonChecklistItem, pk=item_id, lesson=lesson
    )
    progress, _ = TrainingChecklistProgress.objects.get_or_create(
        enrollment=enrollment, checklist_item=checklist_item
    )
    progress.is_done = not progress.is_done
    progress.save(update_fields=["is_done", "updated_at"])
    messages.success(request, "Checklist mise à jour.")
    redirect_target = request.POST.get("next") or "training_lesson"
    if redirect_target == "training_program":
        return redirect("training_program", program_id=lesson.week.program_id)
    return redirect("training_lesson", lesson_id=lesson_id)


@login_required
def training_complete_lesson(request, lesson_id):
    lesson = get_object_or_404(TrainingLesson, pk=lesson_id)
    enrollment = TrainingEnrollment.objects.filter(
        program=lesson.week.program, user=request.user
    ).first()
    if not enrollment:
        messages.error(request, "Veuillez démarrer la formation d'abord.")
        return redirect("training_home")

    completion_status = lesson_completion_status(request.user, lesson)
    if (
        lesson.completion_mode != TrainingLesson.CompletionMode.MANUAL
        and not completion_status["is_eligible"]
    ):
        missing = completion_status["missing_display"] or "des éléments requis"
        messages.error(request, f"Impossible de valider ce module : il manque {missing}.")
        return redirect("training_lesson", lesson_id=lesson.id)

    progress, _ = TrainingProgress.objects.get_or_create(
        enrollment=enrollment, lesson=lesson
    )
    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save(update_fields=["completed", "completed_at"])
    enrollment.refresh_status()
    messages.success(request, "Module validé.")
    return redirect("training_program", program_id=lesson.week.program_id)


@login_required
def training_evaluation(request, program_id):
    program = get_object_or_404(TrainingProgram, pk=program_id)
    enrollment = TrainingEnrollment.objects.filter(
        program=program, user=request.user
    ).first()
    if not enrollment:
        messages.error(request, "Veuillez démarrer la formation d'abord.")
        return redirect("training_home")

    evaluation = TrainingEvaluation.objects.filter(enrollment=enrollment).first()
    if request.method == "POST":
        form = TrainingEvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.enrollment = enrollment
            evaluation.save()
            messages.success(request, "Évaluation enregistrée.")
            return redirect("training_program", program_id=program.id)
        messages.error(request, "Veuillez corriger les champs.")
    else:
        form = TrainingEvaluationForm(instance=evaluation)

    return render(
        request,
        "training/evaluation.html",
        {
            "titre": "Évaluation",
            "page_theme": "training",
            "program": program,
            "form": form,
            "evaluation": evaluation,
            "progress_percent": enrollment.get_progress_percent(),
        },
    )
