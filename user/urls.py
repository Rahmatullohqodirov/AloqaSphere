from django.urls import path
from . import views

urlpatterns = [
    path("send/code/email/",views.SendEmailView.as_view()),
    path("save/",views.UserSaveView.as_view()),
    path("login/",views.LoginView.as_view()),
    path("role/<int:pk>/",views.RoleObjectView.as_view()),
    path("role/",views.RoleView.as_view()) 
]