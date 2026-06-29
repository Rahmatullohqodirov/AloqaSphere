from django.urls import path
from . import views

urlpatterns = [
    path("send/code/email/",views.SendEmailView.as_view()),
    path("save/",views.UserSaveView.as_view()),
    path("login/",views.LoginView.as_view())
    
]