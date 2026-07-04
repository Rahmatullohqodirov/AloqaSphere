from django.urls import path
from . import views

urlpatterns = [
    path("staff/",views.RoleByUserView.as_view()),
    path("report/", views.ReportView.as_view()),
]