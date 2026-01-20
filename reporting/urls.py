from django.urls import path

from reporting.views import dashboard_rendement

urlpatterns = [
    path("dashboard/rendement", dashboard_rendement, name="dashboard-rendement"),
]
