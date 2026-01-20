from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("lms", "0005_alter_assignmentsubmission_feedback_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="badge",
            name="assignment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="badges",
                to="lms.assignment",
                verbose_name="Devoir",
            ),
        ),
        migrations.AddIndex(
            model_name="badge",
            index=models.Index(fields=["assignment"], name="lms_badge_assignment_idx"),
        ),
    ]
