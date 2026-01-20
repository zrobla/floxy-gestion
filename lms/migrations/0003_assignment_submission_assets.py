# Generated manually for assignment submissions assets & review fields
import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("lms", "0002_coursecompletionrule_coursemodule_lessonprogress_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name="assignmentsubmission",
            old_name="reviewer_notes",
            new_name="feedback",
        ),
        migrations.AddField(
            model_name="assignmentsubmission",
            name="reviewed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="lms_reviewed_assignments",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Validé par",
            ),
        ),
        migrations.CreateModel(
            name="AssignmentSubmissionAttachment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                (
                    "image",
                    models.ImageField(upload_to="lms/assignment_attachments/", verbose_name="Image"),
                ),
                (
                    "caption",
                    models.CharField(blank=True, max_length=255, verbose_name="Légende"),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="lms.assignmentsubmission",
                        verbose_name="Soumission",
                    ),
                ),
            ],
            options={
                "verbose_name": "Pièce jointe",
                "verbose_name_plural": "Pièces jointes",
            },
        ),
        migrations.CreateModel(
            name="AssignmentSubmissionLink",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("url", models.URLField(verbose_name="Lien de preuve")),
                (
                    "label",
                    models.CharField(blank=True, max_length=200, verbose_name="Libellé"),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="proof_links",
                        to="lms.assignmentsubmission",
                        verbose_name="Soumission",
                    ),
                ),
            ],
            options={
                "verbose_name": "Lien de preuve",
                "verbose_name_plural": "Liens de preuve",
            },
        ),
        migrations.CreateModel(
            name="AssignmentSubmissionKPI",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
                ("label", models.CharField(max_length=200, verbose_name="KPI")),
                (
                    "value",
                    models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Valeur"),
                ),
                ("unit", models.CharField(blank=True, max_length=50, verbose_name="Unité")),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="kpi_values",
                        to="lms.assignmentsubmission",
                        verbose_name="Soumission",
                    ),
                ),
            ],
            options={
                "verbose_name": "KPI soumission",
                "verbose_name_plural": "KPIs soumission",
            },
        ),
        migrations.AddIndex(
            model_name="assignmentsubmissionattachment",
            index=models.Index(fields=["submission"], name="lms_submission_attach_idx"),
        ),
        migrations.AddIndex(
            model_name="assignmentsubmissionlink",
            index=models.Index(fields=["submission"], name="lms_submission_link_idx"),
        ),
        migrations.AddIndex(
            model_name="assignmentsubmissionkpi",
            index=models.Index(fields=["submission"], name="lms_submission_kpi_idx"),
        ),
    ]
