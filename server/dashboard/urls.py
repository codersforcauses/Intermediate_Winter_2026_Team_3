from django.urls import path
from .views import DashboardView

urlpatterns = [path("api/dashboard/", DashboardView.as_view(), name="dashboard-api")]
