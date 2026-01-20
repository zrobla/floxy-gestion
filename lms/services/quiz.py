from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from lms.models import Choice, Question, Quiz, Submission, SubmissionAnswer


def _normalize_text(value: str, case_sensitive: bool) -> str:
    value = (value or "").strip()
    return value if case_sensitive else value.lower()


@transaction.atomic
def score_quiz_attempt(enrollment, quiz: Quiz, answers: list[dict]) -> Submission:
    if quiz.max_attempts:
        attempt_count = Submission.objects.filter(
            enrollment=enrollment, quiz=quiz
        ).count()
        if attempt_count >= quiz.max_attempts:
            raise ValidationError("Nombre maximal de tentatives atteint.")
    attempt_number = (
        Submission.objects.filter(enrollment=enrollment, quiz=quiz).count() + 1
    )

    submission = Submission.objects.create(
        enrollment=enrollment,
        quiz=quiz,
        attempt_number=attempt_number,
    )

    answers_map = {item.get("question_id"): item for item in answers}
    questions = list(Question.objects.filter(quiz=quiz).prefetch_related("choices"))

    for question in questions:
        payload = answers_map.get(question.id, {})
        selected_choice_id = payload.get("choice_id")
        text_answer = payload.get("text_answer", "") or ""

        selected_choice = None
        if selected_choice_id:
            selected_choice = Choice.objects.filter(
                id=selected_choice_id, question=question
            ).first()

        SubmissionAnswer.objects.create(
            attempt=submission,
            question=question,
            selected_choice=selected_choice,
            text_answer=text_answer if question.question_type == Question.QuestionType.SHORT else "",
        )

    compute_score(submission)
    return submission


@transaction.atomic
def compute_score(submission: Submission) -> Submission:
    questions = list(Question.objects.filter(quiz=submission.quiz))
    answers = {answer.question_id: answer for answer in submission.answers.select_related("question", "selected_choice")}
    max_score = Decimal("0.00")
    total_score = Decimal("0.00")

    for question in questions:
        max_score += Decimal(question.points)
        answer = answers.get(question.id)
        if not answer:
            continue

        is_correct = False
        awarded = Decimal("0.00")

        if question.question_type in {
            Question.QuestionType.MCQ,
            Question.QuestionType.TRUE_FALSE,
        }:
            if answer.selected_choice and answer.selected_choice.is_correct:
                is_correct = True
                awarded = Decimal(question.points)
        elif question.question_type == Question.QuestionType.SHORT:
            if question.manual_review_required:
                if answer.manual_scored:
                    awarded = Decimal(answer.score_awarded or 0)
                    is_correct = answer.is_correct
                else:
                    awarded = Decimal("0.00")
                    is_correct = False
            elif question.correct_text:
                normalized = _normalize_text(answer.text_answer, question.case_sensitive)
                expected = _normalize_text(question.correct_text, question.case_sensitive)
                if normalized == expected:
                    is_correct = True
                    awarded = Decimal(question.points)

        if not (question.question_type == Question.QuestionType.SHORT and question.manual_review_required and answer.manual_scored):
            answer.is_correct = is_correct
            answer.score_awarded = awarded
            answer.save(update_fields=["is_correct", "score_awarded"])

        total_score += awarded

    submission.score = total_score
    submission.max_score = max_score
    achieved_percent = (total_score / max_score * 100) if max_score else Decimal("0.00")
    submission.passed = achieved_percent >= Decimal(submission.quiz.passing_score)
    submission.save(update_fields=["score", "max_score", "passed"])
    from lms.services.progress import update_progress_for_quiz

    update_progress_for_quiz(submission)
    return submission
