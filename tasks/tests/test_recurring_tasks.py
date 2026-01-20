from django.core.management import call_command
from django.test import TestCase

from tasks.models import RecurrenceRule, Task, TaskTemplate


class RecurringTaskCommandTests(TestCase):
    def test_generate_recurring_tasks_is_idempotent(self):
        rule = RecurrenceRule.objects.create(
            name="Quotidien",
            frequency=RecurrenceRule.Frequency.DAILY,
            interval=1,
        )
        template = TaskTemplate.objects.create(
            name="Routine quotidienne",
            description="Tâche test",
            recurrence_rule=rule,
        )

        call_command("generate_recurring_tasks")
        self.assertEqual(Task.objects.filter(template=template).count(), 1)

        call_command("generate_recurring_tasks")
        self.assertEqual(Task.objects.filter(template=template).count(), 1)
