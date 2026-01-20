from django.db import migrations, models


def _column_exists(introspection, table_name: str, column_name: str) -> bool:
    try:
        with introspection.connection.cursor() as cursor:
            columns = [col.name for col in introspection.get_table_description(cursor, table_name)]
    except Exception:
        return False
    return column_name in columns


def _index_exists(introspection, table_name: str, index_name: str) -> bool:
    try:
        with introspection.connection.cursor() as cursor:
            constraints = introspection.get_constraints(cursor, table_name)
        return index_name in constraints
    except Exception:
        return False


def _add_column(schema_editor, table_name: str, column_name: str, column_type: str, default_sql: str):
    schema_editor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {default_sql}"
    )


def ensure_progress_fields(apps, schema_editor):
    introspection = schema_editor.connection.introspection
    existing_tables = set(introspection.table_names())

    Quiz = apps.get_model("lms", "Quiz")
    Progress = apps.get_model("lms", "Progress")
    Assignment = apps.get_model("lms", "Assignment")

    # Quiz.is_required_for_completion
    if Quiz._meta.db_table not in existing_tables:
        schema_editor.create_model(Quiz)
    if Quiz._meta.db_table in existing_tables and not _column_exists(
        introspection, Quiz._meta.db_table, "is_required_for_completion"
    ):
        _add_column(
            schema_editor,
            Quiz._meta.db_table,
            "is_required_for_completion",
            "integer",
            "DEFAULT 0",
        )

    # Progress.viewed_at / quiz_passed
    if Progress._meta.db_table not in existing_tables:
        schema_editor.create_model(Progress)
    if Progress._meta.db_table in existing_tables:
        if not _column_exists(introspection, Progress._meta.db_table, "viewed_at"):
            _add_column(
                schema_editor,
                Progress._meta.db_table,
                "viewed_at",
                "datetime",
                "NULL",
            )
        if not _column_exists(introspection, Progress._meta.db_table, "quiz_passed"):
            _add_column(
                schema_editor,
                Progress._meta.db_table,
                "quiz_passed",
                "integer",
                "DEFAULT 0",
            )

    # Assignment.is_final_assessment + index
    if Assignment._meta.db_table not in existing_tables:
        schema_editor.create_model(Assignment)
    if Assignment._meta.db_table in existing_tables and not _column_exists(
        introspection, Assignment._meta.db_table, "is_final_assessment"
    ):
        _add_column(
            schema_editor,
            Assignment._meta.db_table,
            "is_final_assessment",
            "integer",
            "DEFAULT 0",
        )

    if Assignment._meta.db_table in existing_tables:
        index_name = "lms_assignment_final_idx"
        if not _index_exists(introspection, Assignment._meta.db_table, index_name):
            schema_editor.execute(
                f"CREATE INDEX {index_name} ON {Assignment._meta.db_table} (is_final_assessment)"
            )


class Migration(migrations.Migration):
    dependencies = [
        ("lms", "0003_assignment_submission_assets"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunPython(ensure_progress_fields, migrations.RunPython.noop)],
            state_operations=[
                migrations.AddField(
                    model_name="quiz",
                    name="is_required_for_completion",
                    field=models.BooleanField(
                        default=False, verbose_name="Requis pour la complétion"
                    ),
                ),
                migrations.AddField(
                    model_name="progress",
                    name="viewed_at",
                    field=models.DateTimeField(
                        blank=True, null=True, verbose_name="Vu le"
                    ),
                ),
                migrations.AddField(
                    model_name="progress",
                    name="quiz_passed",
                    field=models.BooleanField(default=False, verbose_name="Quiz validé"),
                ),
                migrations.AddField(
                    model_name="assignment",
                    name="is_final_assessment",
                    field=models.BooleanField(default=False, verbose_name="Évaluation finale"),
                ),
                migrations.AddIndex(
                    model_name="assignment",
                    index=models.Index(
                        fields=["is_final_assessment"], name="lms_assignment_final_idx"
                    ),
                ),
            ],
        ),
    ]
