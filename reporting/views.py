from datetime import timedelta

from django.db import models
from django.db.models import Avg, Count, F, FloatField, Value
from django.db.models.functions import Cast, TruncDate
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from content.models import ContentApproval, ContentItem, ContentMetric
from reporting.permissions import OwnerAdminPermission
from tasks.models import Task


@api_view(["GET"])
@permission_classes([OwnerAdminPermission])
def dashboard_rendement(request):
    today = timezone.localdate()
    since_date = today - timedelta(days=6)

    done_tasks = Task.objects.filter(
        status=Task.Status.DONE, updated_at__date__gte=since_date
    ).annotate(done_date=TruncDate("updated_at"))
    late_tasks = done_tasks.filter(due_date__isnull=False, due_date__lt=F("done_date"))

    content_items = ContentItem.objects.filter(created_at__date__gte=since_date)
    platform_counts = content_items.values("platform").annotate(count=Count("id"))
    platform_summary = {
        ContentItem.Platform(item["platform"]).label: item["count"]
        for item in platform_counts
    }

    approvals = ContentApproval.objects.filter(created_at__date__gte=since_date)
    submitted = approvals.count()
    approved = approvals.filter(approved=True).count()
    approval_rate = round((approved / submitted) * 100, 2) if submitted else 0.0

    interactions = F("likes") + F("comments") + F("shares") + F("saves")
    score_expr = models.Case(
        models.When(
            reach__gt=0,
            then=Cast(interactions, FloatField())
            * Value(100.0)
            / Cast(F("reach"), FloatField()),
        ),
        default=Cast(interactions, FloatField()),
        output_field=FloatField(),
    )

    metrics_queryset = ContentMetric.objects.filter(
        content_item__status__in=[
            ContentItem.Status.PUBLISHED,
            ContentItem.Status.METRICS_RECORDED,
        ],
        created_at__date__gte=since_date,
    )
    average_score = (
        metrics_queryset.annotate(score=score_expr).aggregate(avg=Avg("score"))["avg"]
        or 0.0
    )
    average_score = round(float(average_score), 2)

    return Response(
        {
            "taches": {
                "terminees": done_tasks.count(),
                "en_retard": late_tasks.count(),
            },
            "contenus_par_plateforme": platform_summary,
            "taux_validation": {
                "approuves": approved,
                "soumis": submitted,
                "taux": approval_rate,
            },
            "score_moyen_contenu": average_score,
        }
    )
