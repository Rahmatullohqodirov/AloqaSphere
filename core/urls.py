from django.urls import path
from .views import LeaderBoardView, ScoreUpView, DashboardView

urlpatterns = [
    path('/leaderboard/', LeaderBoardView.as_view(), name='leaderboard'),
    path('score-up/', ScoreUpView.as_view(), name='score-up'),
    path('dashboard/', DashboardView.as_view(), name='dashboard-stats'),
]