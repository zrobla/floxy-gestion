from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.db import models
from django.db.models import (
    Avg,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    FloatField,
    Sum,
    Value,
)
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from content.models import ContentItem, ContentMetric
from floxy.forms import (
    ActivityForm,
    ActivityStatusForm,
    CareWigForm,
    ContentItemForm,
    PrestationsPOSForm,
    TaskChecklistForm,
    TaskForm,
)
from floxy.prestations import (
    get_prestation_cards,
    get_prestation_filters,
    get_service_ids_for_category,
)
from crm.models import Client
from operations.models import Activity, ActivityLine, Service
from inventory.models import StockLevel
from tasks.models import Task
from wigs.models import CareWig


@login_required
def profile_view(request):
    return render(
        request,
        "profile.html",
        {
        "titre": "Profil",
        "auth_required": False,
        "page_theme": "profile",
        },
    )


def _role_in(user, roles):
    return bool(user and user.is_authenticated and user.role in roles)


@login_required
def dashboard_overview(request):
    today = timezone.localdate()
    start_param = request.GET.get("start")
    end_param = request.GET.get("end")
    service_filter = request.GET.get("service")
    sector_filter = request.GET.get("sector")
    custom_range = False
    dashboard_error = None

    start_date = None
    end_date = None
    def _parse_date(value: str):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError

    if start_param and end_param:
        try:
            start_date = _parse_date(start_param)
            end_date = _parse_date(end_param)
            custom_range = True
        except ValueError:
            dashboard_error = "Période invalide. Utilisez jj/mm/aaaa."
            messages.error(request, dashboard_error)
            start_date = None
            end_date = None

    if not start_date or not end_date:
        try:
            period_days = int(request.GET.get("days", 30))
        except ValueError:
            period_days = 30
        if period_days not in {7, 30, 90}:
            period_days = 30
        end_date = today
        start_date = today - timezone.timedelta(days=period_days - 1)
    else:
        period_days = (end_date - start_date).days + 1
        if period_days <= 0:
            dashboard_error = (
                "Période invalide. La date de fin doit suivre le début."
            )
            messages.error(request, dashboard_error)
            end_date = today
            start_date = today - timezone.timedelta(days=29)
            period_days = 30
            custom_range = False

    activities_period = Activity.objects.filter(
        start_at__date__gte=start_date, start_at__date__lte=end_date
    )
    activities_paid = activities_period.filter(status=Activity.Status.PAID)
    service_queryset = Service.objects.filter(is_active=True)
    if service_filter:
        service_queryset = service_queryset.filter(id=service_filter)
    elif sector_filter:
        service_ids = get_service_ids_for_category(sector_filter)
        service_queryset = service_queryset.filter(id__in=service_ids)

    if service_filter or sector_filter:
        service_ids = list(service_queryset.values_list("id", flat=True))
        if service_ids:
            activities_period = activities_period.filter(
                lines__service_id__in=service_ids
            ).distinct()
            activities_paid = activities_paid.filter(
                lines__service_id__in=service_ids
            ).distinct()
        else:
            activities_period = activities_period.none()
            activities_paid = activities_paid.none()
    activities_total = activities_period.count()
    revenue_expected = (
        activities_period.aggregate(total=Sum("expected_amount"))["total"] or 0
    )
    revenue_final = (
        activities_paid.aggregate(total=Sum("final_amount"))["total"] or 0
    )

    tasks_period = Task.objects.filter(
        created_at__date__gte=start_date, created_at__date__lte=end_date
    )
    tasks_done = Task.objects.filter(
        status=Task.Status.DONE,
        updated_at__date__gte=start_date,
        updated_at__date__lte=end_date,
    ).count()
    tasks_total = tasks_period.count()
    tasks_completion_rate = (
        round((tasks_done / tasks_total) * 100, 2) if tasks_total else 0
    )
    tasks_overdue = Task.objects.filter(
        due_date__lt=today, status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]
    ).count()

    content_period = ContentItem.objects.filter(
        created_at__date__gte=start_date, created_at__date__lte=end_date
    )
    platform_counts = content_period.values("platform").annotate(count=Count("id"))
    platform_breakdown = [
        {
            "label": ContentItem.Platform(item["platform"]).label,
            "count": item["count"],
        }
        for item in platform_counts
    ]
    content_approved = content_period.filter(status=ContentItem.Status.APPROVED).count()
    content_published = content_period.filter(
        status__in=[ContentItem.Status.PUBLISHED, ContentItem.Status.METRICS_RECORDED]
    ).count()

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
    average_score = ContentMetric.objects.filter(
        content_item__status__in=[
            ContentItem.Status.PUBLISHED,
            ContentItem.Status.METRICS_RECORDED,
        ],
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
    ).annotate(score=score_expr).aggregate(avg=Avg("score"))["avg"] or 0.0

    line_total_expr = ExpressionWrapper(
        F("quantity") * F("unit_price"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    service_summary_queryset = ActivityLine.objects.filter(
        activity__start_at__date__gte=start_date,
        activity__start_at__date__lte=end_date,
        activity__status=Activity.Status.PAID,
        service__isnull=False,
    )
    if service_filter or sector_filter:
        service_ids = list(service_queryset.values_list("id", flat=True))
        if service_ids:
            service_summary_queryset = service_summary_queryset.filter(
                service_id__in=service_ids
            )
        else:
            service_summary_queryset = service_summary_queryset.none()

    service_summary = (
        service_summary_queryset
        .values("service__name")
        .annotate(
            total_lines=Count("id"),
            total_qty=Sum("quantity"),
            revenue=Sum(line_total_expr),
        )
        .order_by("-revenue")
    )
    prestations_breakdown = []
    for item in service_summary:
        revenue = item["revenue"] or 0
        total_lines = item["total_lines"] or 0
        avg_ticket = round(float(revenue / total_lines), 2) if total_lines else 0
        prestations_breakdown.append(
            {
                "name": item["service__name"],
                "total_lines": total_lines,
                "total_qty": item["total_qty"] or 0,
                "revenue": revenue,
                "avg_ticket": avg_ticket,
            }
        )

    prestation_filters = get_prestation_filters()
    context = {
        "titre": "Dashboard",
        "auth_required": False,
        "page_theme": "dashboard",
        "period_days": period_days,
        "start_date": start_date,
        "end_date": end_date,
        "custom_range": custom_range,
        "start_input": start_param or start_date.strftime("%d/%m/%Y"),
        "end_input": end_param or end_date.strftime("%d/%m/%Y"),
        "dashboard_error": dashboard_error,
        "selected_service": service_filter or "",
        "selected_sector": sector_filter or "",
        "prestation_services": prestation_filters["services"],
        "prestation_categories": prestation_filters["categories"],
        "activities_total": activities_total,
        "activities_paid": activities_paid.count(),
        "revenue_expected": revenue_expected,
        "revenue_final": revenue_final,
        "tasks_done": tasks_done,
        "tasks_total": tasks_total,
        "tasks_overdue": tasks_overdue,
        "tasks_completion_rate": tasks_completion_rate,
        "content_total": content_period.count(),
        "content_approved": content_approved,
        "content_published": content_published,
        "content_score_avg": round(float(average_score), 2),
        "platform_breakdown": platform_breakdown,
        "prestations_breakdown": prestations_breakdown,
    }
    return render(request, "dashboard_overview.html", context)


@login_required
def dashboard_today(request):
    today = timezone.localdate()
    activities_today_qs = Activity.objects.filter(start_at__date=today)
    tasks_due_qs = Task.objects.filter(due_date=today)
    tasks_overdue_qs = Task.objects.filter(
        due_date__lt=today, status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]
    )
    content_today_qs = ContentItem.objects.filter(scheduled_at__date=today)
    activities_to_collect = Activity.objects.filter(status=Activity.Status.TO_COLLECT)
    expected_revenue = (
        activities_today_qs.aggregate(total=Sum("expected_amount"))["total"] or 0
    )
    line_total_expr = ExpressionWrapper(
        F("quantity") * F("unit_price"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    today_lines = (
        ActivityLine.objects.filter(
            activity__start_at__date=today,
            service__isnull=False,
        )
        .select_related(
            "activity", "service", "service__category", "activity__assigned_staff"
        )
        .order_by("activity__start_at")
    )
    today_prestations_summary = (
        today_lines.values("service__name")
        .annotate(
            total_lines=Count("id"),
            total_qty=Sum("quantity"),
            revenue=Sum(line_total_expr),
        )
        .order_by("-total_lines")
    )
    prestations_today = []
    for item in today_prestations_summary:
        revenue = item["revenue"] or 0
        total_lines = item["total_lines"] or 0
        avg_ticket = round(float(revenue / total_lines), 2) if total_lines else 0
        prestations_today.append(
            {
                "name": item["service__name"],
                "total_lines": total_lines,
                "total_qty": item["total_qty"] or 0,
                "revenue": revenue,
                "avg_ticket": avg_ticket,
            }
        )
    prestations_schedule = list(today_lines[:10])
    for line in prestations_schedule:
        line.total_amount = (line.quantity or 0) * (line.unit_price or 0)
    category_summary = (
        today_lines.values("service__category__name")
        .annotate(
            total_lines=Count("id"),
            total_qty=Sum("quantity"),
            revenue=Sum(line_total_expr),
        )
        .order_by("-total_lines")
    )
    prestations_categories = []
    for item in category_summary:
        category_name = item["service__category__name"] or "Autres"
        total_lines = item["total_lines"] or 0
        revenue = item["revenue"] or 0
        avg_ticket = round(float(revenue / total_lines), 2) if total_lines else 0
        prestations_categories.append(
            {
                "name": category_name,
                "total_lines": total_lines,
                "total_qty": item["total_qty"] or 0,
                "revenue": revenue,
                "avg_ticket": avg_ticket,
            }
        )
    context = {
        "titre": "Aujourd'hui",
        "auth_required": not request.user.is_authenticated,
        "page_theme": "dashboard",
        "activities_today": activities_today_qs.count(),
        "tasks_due": tasks_due_qs.count(),
        "content_scheduled": content_today_qs.count(),
        "expected_revenue": expected_revenue,
        "activities_summary": {
            "in_progress": Activity.objects.filter(
                status=Activity.Status.IN_PROGRESS
            ).count(),
            "to_collect": activities_to_collect.count(),
            "paid": Activity.objects.filter(status=Activity.Status.PAID).count(),
            "done": Activity.objects.filter(status=Activity.Status.DONE).count(),
        },
        "tasks_summary": {
            "overdue": tasks_overdue_qs.count(),
            "done": Task.objects.filter(status=Task.Status.DONE).count(),
        },
        "content_summary": {
            "to_validate": ContentItem.objects.filter(
                status=ContentItem.Status.TO_VALIDATE
            ).count(),
            "scheduled": ContentItem.objects.filter(
                status=ContentItem.Status.SCHEDULED
            ).count(),
        },
        "care_wigs_summary": {
            "in_progress": CareWig.objects.filter(
                status=CareWig.Status.IN_PROGRESS
            ).count(),
            "ready": CareWig.objects.filter(status=CareWig.Status.READY).count(),
            "delivered": CareWig.objects.filter(
                status=CareWig.Status.DELIVERED
            ).count(),
        },
        "stock_alerts": StockLevel.objects.filter(alert=True).count(),
        "activities_recent": Activity.objects.order_by("-start_at")[:5],
        "tasks_overdue_list": tasks_overdue_qs.order_by("due_date")[:5],
        "content_queue": ContentItem.objects.filter(
            status=ContentItem.Status.TO_VALIDATE
        ).order_by("-created_at")[:5],
        "care_wigs_ready": CareWig.objects.filter(
            status=CareWig.Status.READY
        ).order_by("-created_at")[:5],
        "stock_alerts_list": StockLevel.objects.filter(alert=True)
        .select_related("item")
        .order_by("-updated_at")[:5],
        "prestations_today": prestations_today,
        "prestations_categories": prestations_categories,
        "prestations_schedule": prestations_schedule,
    }
    return render(request, "dashboard.html", context)


@login_required
def activities_view(request):
    can_manage = _role_in(request.user, {"OWNER", "MANAGER", "ADMIN"})
    activities = (
        Activity.objects.select_related("assigned_staff")
        .prefetch_related("lines__service")
        .order_by("-start_at")
    )

    if request.method == "POST" and can_manage:
        if "create_activity" in request.POST:
            form = ActivityForm(request.POST)
            if form.is_valid():
                activity = form.save(commit=False)
                service = form.cleaned_data.get("service")
                quantity = form.cleaned_data.get("quantity") or 1
                unit_price = form.cleaned_data.get("unit_price")
                if service:
                    unit_price = unit_price if unit_price is not None else service.base_price
                    activity.expected_amount = Decimal(unit_price) * Decimal(quantity)
                elif activity.expected_amount is None:
                    activity.expected_amount = 0
                activity.save()
                if service:
                    ActivityLine.objects.create(
                        activity=activity,
                        service=service,
                        quantity=quantity,
                        unit_price=unit_price,
                    )
                messages.success(request, "Enregistré")
                return redirect("activities")
            messages.error(request, "Veuillez corriger les champs.")
        elif "update_status" in request.POST:
            activity = get_object_or_404(Activity, pk=request.POST.get("activity_id"))
            status_form = ActivityStatusForm(request.POST, instance=activity)
            if status_form.is_valid():
                activity.set_status(status_form.cleaned_data["status"])
                messages.success(request, "Enregistré")
                return redirect("activities")
            messages.error(request, "Veuillez corriger les champs.")

    for activity in activities:
        first_line = activity.lines.first()
        activity.primary_service = first_line.service if first_line else None

    context = {
        "titre": "Activités",
        "auth_required": not request.user.is_authenticated,
        "page_theme": "activities",
        "can_manage": can_manage,
        "activities": activities,
        "form": ActivityForm(),
        "status_form": ActivityStatusForm(),
        "open_form": request.method == "POST",
        "prestations": get_prestation_cards(),
    }
    return render(request, "activities.html", context)


@login_required
def prestations_view(request):
    can_manage = _role_in(request.user, {"OWNER", "MANAGER", "ADMIN"})
    service_id = request.GET.get("service")
    initial = {"type": Activity.Type.SERVICE}
    if service_id:
        service = Service.objects.filter(pk=service_id, is_active=True).first()
        if service:
            initial.update({"services": [str(service.id)], "unit_price": service.base_price})

    form = PrestationsPOSForm(initial=initial)
    if request.method == "POST" and can_manage:
        form = PrestationsPOSForm(request.POST)
        if form.is_valid():
            client_existing = form.cleaned_data.get("client_existing")
            client_name = form.cleaned_data.get("client_name", "").strip()
            client_phone = form.cleaned_data.get("client_phone", "").strip()
            if client_existing:
                client_label = client_existing.name
            else:
                client_label = client_name
                Client.objects.get_or_create(
                    name=client_name,
                    defaults={"phone": client_phone},
                )

            activity = Activity.objects.create(
                type=form.cleaned_data["type"],
                client=client_label,
                assigned_staff=form.cleaned_data.get("assigned_staff"),
                expected_amount=0,
                notes=form.cleaned_data.get("notes", ""),
                content_possible=form.cleaned_data.get("content_possible", False),
            )

            services = form.cleaned_data.get("services") or []
            quantity = form.cleaned_data.get("quantity") or 1
            unit_price = form.cleaned_data.get("unit_price")
            if activity.type == Activity.Type.SERVICE and services:
                total_amount = Decimal("0")
                for service in services:
                    line_price = unit_price if unit_price is not None else service.base_price
                    ActivityLine.objects.create(
                        activity=activity,
                        service=service,
                        quantity=quantity,
                        unit_price=line_price,
                    )
                    total_amount += Decimal(line_price) * Decimal(quantity)
                activity.expected_amount = total_amount
                activity.save(update_fields=["expected_amount", "updated_at"])
            elif activity.type == Activity.Type.PRODUCT_PURCHASE:
                activity.expected_amount = form.cleaned_data.get("expected_amount") or 0
                activity.save(update_fields=["expected_amount", "updated_at"])
            messages.success(request, "Enregistré")
            return redirect("prestations")
        messages.error(request, "Veuillez corriger les champs.")

    today = timezone.localdate()
    activities_today = (
        Activity.objects.filter(start_at__date=today)
        .prefetch_related("lines__service")
        .order_by("-start_at")[:10]
    )
    for activity in activities_today:
        first_line = activity.lines.first()
        activity.primary_service = first_line.service if first_line else None
    expected_total = (
        Activity.objects.filter(start_at__date=today).aggregate(total=Sum("expected_amount"))[
            "total"
        ]
        or 0
    )
    paid_total = (
        Activity.objects.filter(
            start_at__date=today, status=Activity.Status.PAID
        ).aggregate(total=Sum("final_amount"))["total"]
        or 0
    )

    context = {
        "titre": "Prestations",
        "auth_required": not request.user.is_authenticated,
        "page_theme": "activities",
        "can_manage": can_manage,
        "form": form,
        "prestations": get_prestation_cards(),
        "activities_today": activities_today,
        "expected_total": expected_total,
        "paid_total": paid_total,
        "open_form": request.method == "POST",
    }
    return render(request, "prestations.html", context)


@login_required
def care_wigs_view(request):
    can_manage = _role_in(request.user, {"OWNER", "MANAGER", "ADMIN"})
    items = CareWig.objects.order_by("-created_at")

    if request.method == "POST" and can_manage:
        form = CareWigForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Enregistré")
            return redirect("care_wigs")
        messages.error(request, "Veuillez corriger les champs.")

    context = {
        "titre": "Entretien perruques",
        "auth_required": not request.user.is_authenticated,
        "page_theme": "care",
        "can_manage": can_manage,
        "items": items,
        "form": CareWigForm(),
        "open_form": request.method == "POST",
    }
    return render(request, "care_wigs.html", context)


@login_required
def tasks_view(request):
    can_manage = _role_in(request.user, {"OWNER", "MANAGER", "ADMIN"})
    if request.user.is_authenticated and request.user.role == "STAFF":
        tasks = Task.objects.filter(assigned_to=request.user)
    else:
        tasks = Task.objects.all()
    tasks = tasks.select_related("assigned_to").prefetch_related("checklist_items")
    tasks = tasks.order_by("-created_at")

    today = timezone.localdate()
    for task in tasks:
        task.is_overdue = bool(task.due_date and task.due_date < today)

    if request.method == "POST":
        if "create_task" in request.POST and can_manage:
            form = TaskForm(request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.created_by = request.user
                task.save()
                messages.success(request, "Enregistré")
                return redirect("tasks")
            messages.error(request, "Veuillez corriger les champs.")
        if "add_checklist" in request.POST and can_manage:
            task = get_object_or_404(Task, pk=request.POST.get("task_id"))
            checklist_form = TaskChecklistForm(request.POST)
            if checklist_form.is_valid():
                item = checklist_form.save(commit=False)
                item.task = task
                item.save()
                messages.success(request, "Enregistré")
                return redirect("tasks")
            messages.error(request, "Veuillez corriger les champs.")
        if "set_status" in request.POST:
            task = get_object_or_404(Task, pk=request.POST.get("task_id"))
            if request.user.role == "STAFF" and task.assigned_to_id != request.user.id:
                return redirect("tasks")
            if request.user.role == "STAFF" or can_manage:
                new_status = request.POST.get("status")
                if new_status:
                    try:
                        task.set_status(new_status)
                        messages.success(request, "Enregistré")
                        return redirect("tasks")
                    except ValidationError:
                        messages.error(request, "Veuillez corriger les champs.")
                else:
                    messages.error(request, "Veuillez corriger les champs.")

    context = {
        "titre": "Tâches",
        "auth_required": not request.user.is_authenticated,
        "page_theme": "tasks",
        "can_manage": can_manage,
        "tasks": tasks,
        "form": TaskForm(),
        "checklist_form": TaskChecklistForm(),
        "open_form": request.method == "POST",
    }
    return render(request, "tasks.html", context)


@login_required
def content_calendar_view(request):
    can_manage = _role_in(request.user, {"OWNER", "MANAGER", "ADMIN"})
    is_owner = _role_in(request.user, {"OWNER"})

    items = ContentItem.objects.order_by("-created_at")
    queue = items.filter(status=ContentItem.Status.TO_VALIDATE)

    if request.method == "POST":
        if "create_content" in request.POST and can_manage:
            form = ContentItemForm(request.POST)
            if form.is_valid():
                content_item = form.save(commit=False)
                content_item.created_by = request.user
                content_item.save()
                messages.success(request, "Enregistré")
                return redirect("content_calendar")
            messages.error(request, "Veuillez corriger les champs.")
        if "submit_for_approval" in request.POST and can_manage:
            content_item = get_object_or_404(
                ContentItem, pk=request.POST.get("content_id")
            )
            try:
                content_item.submit_for_approval()
                messages.success(request, "Enregistré")
                return redirect("content_calendar")
            except ValidationError:
                messages.error(request, "Veuillez corriger les champs.")
        if "approve" in request.POST and is_owner:
            content_item = get_object_or_404(
                ContentItem, pk=request.POST.get("content_id")
            )
            comment = request.POST.get("comment", "").strip()
            try:
                content_item.approve(request.user, comment)
                messages.success(request, "Enregistré")
                return redirect("content_calendar")
            except ValidationError:
                messages.error(request, "Veuillez corriger les champs.")
        if "reject" in request.POST and is_owner:
            content_item = get_object_or_404(
                ContentItem, pk=request.POST.get("content_id")
            )
            comment = request.POST.get("comment", "").strip()
            try:
                content_item.reject(request.user, comment)
                messages.success(request, "Enregistré")
                return redirect("content_calendar")
            except ValidationError:
                messages.error(request, "Veuillez corriger les champs.")
        if "publish" in request.POST and can_manage:
            content_item = get_object_or_404(
                ContentItem, pk=request.POST.get("content_id")
            )
            try:
                content_item.publish()
                messages.success(request, "Enregistré")
                return redirect("content_calendar")
            except ValidationError:
                messages.error(request, "Veuillez corriger les champs.")

    context = {
        "titre": "Calendrier contenus",
        "auth_required": not request.user.is_authenticated,
        "page_theme": "content",
        "can_manage": can_manage,
        "is_owner": is_owner,
        "items": items,
        "queue": queue,
        "form": ContentItemForm(),
        "open_form": request.method == "POST",
    }
    return render(request, "content_calendar.html", context)
