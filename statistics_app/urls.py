from django.urls import path

from .views import DashboardView, HeatmapView, WeeklyReportView, LeaderboardView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="stats-dashboard"),
    path("heatmap/", HeatmapView.as_view(), name="stats-heatmap"),
    path("weekly-report/", WeeklyReportView.as_view(), name="stats-weekly-report"),
    path("leaderboard/", LeaderboardView.as_view(), name="stats-leaderboard"),
]
