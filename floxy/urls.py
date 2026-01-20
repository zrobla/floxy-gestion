"""Routes principales du projet."""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from rest_framework.schemas import get_schema_view

from floxy.forms import LoginForm
from floxy.views import (
    activities_view,
    care_wigs_view,
    content_calendar_view,
    dashboard_overview,
    dashboard_today,
    prestations_view,
    profile_view,
    tasks_view,
)

urlpatterns = [
    path(
        "",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=LoginForm,
            extra_context={"titre": "Connexion", "page_theme": "profile"},
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=LoginForm,
            extra_context={"titre": "Connexion", "page_theme": "profile"},
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard_overview, name="dashboard"),
    path("aujourdhui/", dashboard_today, name="today"),
    path("activites/", activities_view, name="activities"),
    path("prestations/", prestations_view, name="prestations"),
    path("perruques-entretien/", care_wigs_view, name="care_wigs"),
    path("taches/", tasks_view, name="tasks"),
    path("contenus/", content_calendar_view, name="content_calendar"),
    path("profil/", profile_view, name="profile"),
    path("admin/", admin.site.urls),
    path("api/", include("operations.urls")),
    path("api/wigs/", include("wigs.urls")),
    path("api/inventory/", include("inventory.urls")),
    path("api/tasks/", include("tasks.urls")),
    path("api/content/", include("content.urls")),
    path("api/integrations/", include("integrations.urls")),
    path("api/lms/", include("lms.urls")),
    path("api/schema/", get_schema_view(title="Floxy Made API"), name="api-schema"),
    path("reporting/", include("reporting.urls")),
    path("formation/", include("training.urls")),
    path("wigs/", include("wigs.urls")),
]

urlpatterns += staticfiles_urlpatterns()
