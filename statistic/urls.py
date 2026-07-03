from django.urls import path
from . import views

urlpatterns = [
    path("staff/",views.RoleByUserView.as_view())
]