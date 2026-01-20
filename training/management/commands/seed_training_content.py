import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from training.models import (
    TrainingChoice,
    TrainingLesson,
    TrainingLessonChecklistItem,
    TrainingLessonResource,
    TrainingProgram,
    TrainingQuestion,
    TrainingQuiz,
    TrainingWeek,
)


class Command(BaseCommand):
    help = "Seed training content (program/weeks/lessons/resources/quizzes) from JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="/mnt/data/training_seed_content.json",
            help="Chemin du fichier JSON à importer.",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"Fichier introuvable: {path}")

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"JSON invalide: {exc}") from exc

        program_title = payload.get("program_title")
        program_slug = payload.get("program_slug") or slugify(program_title or "")
        if not program_title:
            raise CommandError("program_title manquant dans le JSON.")

        counts = {
            "programs_created": 0,
            "weeks_created": 0,
            "lessons_created": 0,
            "resources_created": 0,
            "checklists_created": 0,
            "questions_created": 0,
            "choices_created": 0,
        }

        with transaction.atomic():
            program = TrainingProgram.objects.filter(slug=program_slug).first()
            if not program:
                program = TrainingProgram.objects.filter(title=program_title).first()
            if not program:
                program = TrainingProgram.objects.create(
                    title=program_title, slug=program_slug
                )
                counts["programs_created"] += 1
            else:
                if program_slug and not program.slug:
                    program.slug = program_slug
                    program.save(update_fields=["slug"])

            self.stdout.write(f"Programme: {program.title} ({program.slug})")

            weeks_data = payload.get("weeks", [])
            for week_data in weeks_data:
                week_number = week_data.get("week_number")
                week_title = week_data.get("week_title")
                if not week_number or not week_title:
                    self.stdout.write(
                        self.style.WARNING("Semaine ignorée (numéro ou titre manquant).")
                    )
                    continue
                week_objective = week_data.get("week_objective") or week_title

                week, created = TrainingWeek.objects.get_or_create(
                    program=program,
                    week_number=week_number,
                    defaults={"title": week_title, "objective": week_objective},
                )
                if created:
                    counts["weeks_created"] += 1
                else:
                    updates = {}
                    if week.title != week_title:
                        updates["title"] = week_title
                    if week.objective != week_objective:
                        updates["objective"] = week_objective
                    if updates:
                        for field, value in updates.items():
                            setattr(week, field, value)
                        week.save(update_fields=list(updates.keys()))

                lessons_data = week_data.get("lessons", [])
                for index, lesson_data in enumerate(lessons_data, start=1):
                    lesson_title = lesson_data.get("lesson_title")
                    if not lesson_title:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Semaine {week_number}: module ignoré (titre manquant)."
                            )
                        )
                        continue

                    lesson, created = TrainingLesson.objects.get_or_create(
                        week=week, title=lesson_title
                    )
                    if created:
                        counts["lessons_created"] += 1

                    lesson_updates = {}
                    lesson_updates["order"] = index
                    content_md = lesson_data.get("content_md", "")
                    if content_md:
                        lesson_updates["content_md"] = content_md
                    estimated_minutes = lesson_data.get("estimated_minutes")
                    if estimated_minutes is not None:
                        lesson_updates["estimated_minutes"] = estimated_minutes
                    completion_mode = lesson_data.get("completion_mode")
                    if completion_mode:
                        lesson_updates["completion_mode"] = completion_mode
                    passing_score = lesson_data.get("passing_score")
                    if passing_score is not None:
                        lesson_updates["passing_score"] = passing_score
                    lesson_type = lesson_data.get("lesson_type")
                    if lesson_type:
                        lesson_updates["lesson_type"] = lesson_type

                    case_prompt = build_case_prompt(lesson_data.get("case_study"))
                    if case_prompt:
                        lesson_updates["case_prompt_md"] = case_prompt

                    if lesson_updates:
                        for field, value in lesson_updates.items():
                            setattr(lesson, field, value)
                        lesson.save(update_fields=list(lesson_updates.keys()))

                    resource_list = lesson_data.get("resources", [])
                    for resource in resource_list:
                        title = resource.get("title")
                        if not title:
                            continue
                        resource_type = resource.get("resource_type") or TrainingLessonResource.ResourceType.GUIDE
                        description = resource.get("description") or ""
                        content_md = resource.get("content_md") or ""
                        url = resource.get("url") or ""
                        resource_obj, created = TrainingLessonResource.objects.get_or_create(
                            lesson=lesson, title=title
                        )
                        if created:
                            counts["resources_created"] += 1
                        updates = {}
                        if resource_type:
                            updates["resource_type"] = resource_type
                        if description:
                            updates["description"] = description
                        if content_md:
                            updates["content_md"] = content_md
                        if url:
                            updates["url"] = url
                        if updates:
                            for field, value in updates.items():
                                setattr(resource_obj, field, value)
                            resource_obj.save(update_fields=list(updates.keys()))

                    checklist_items = lesson_data.get("checklist", [])
                    for order, label in enumerate(checklist_items, start=1):
                        if not label:
                            continue
                        item, created = TrainingLessonChecklistItem.objects.update_or_create(
                            lesson=lesson,
                            label=label,
                            defaults={"order": order, "is_required": True},
                        )
                        if created:
                            counts["checklists_created"] += 1

                    quiz_data = lesson_data.get("quiz")
                    if quiz_data:
                        quiz, _ = TrainingQuiz.objects.get_or_create(lesson=lesson)
                        quiz.questions.update(is_active=False)

                        for q_index, question in enumerate(
                            quiz_data.get("questions", []), start=1
                        ):
                            question_text = question.get("question_text")
                            if not question_text:
                                continue
                            explanation = question.get("explanation", "")
                            if not explanation and question.get("answer"):
                                explanation = f"Réponse attendue : {question['answer']}"
                            question_obj = TrainingQuestion.objects.create(
                                quiz=quiz,
                                question_text=question_text,
                                question_type=question.get("question_type", "MCQ"),
                                order=q_index,
                                points=question.get("points", 1),
                                explanation=explanation,
                                is_active=True,
                            )
                            counts["questions_created"] += 1
                            choices = question.get("choices") or []
                            for c_index, choice in enumerate(choices, start=1):
                                TrainingChoice.objects.create(
                                    question=question_obj,
                                    choice_text=choice.get("choice_text", ""),
                                    is_correct=choice.get("is_correct", False),
                                    order=c_index,
                                )
                                counts["choices_created"] += 1

        self.stdout.write(self.style.SUCCESS("Import terminé."))
        self.stdout.write(
            "Créés: "
            f"programmes={counts['programs_created']}, "
            f"semaines={counts['weeks_created']}, "
            f"modules={counts['lessons_created']}, "
            f"ressources={counts['resources_created']}, "
            f"checklists={counts['checklists_created']}, "
            f"questions={counts['questions_created']}, "
            f"choix={counts['choices_created']}"
        )


def build_case_prompt(case_study: dict | None) -> str:
    if not case_study:
        return ""
    prompt = (case_study.get("prompt_md") or "").strip()
    rubric = case_study.get("grading_rubric") or []
    if rubric:
        lines = ["", "### Grille de notation"]
        for item in rubric:
            criterion = item.get("criterion")
            points = item.get("points")
            if not criterion:
                continue
            if points is None:
                lines.append(f"- {criterion}")
            else:
                lines.append(f"- {criterion} ({points} pts)")
        prompt = prompt + "\n" + "\n".join(lines)
    return prompt.strip()
