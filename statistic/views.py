from django.shortcuts import render
from rest_framework import generics
from user.models import Role
from .serializers import RoleSerializer
from django.db.models import Count
from .permissions import StatistikaPermission
class RoleByUserView(generics.ListAPIView):
    queryset = Role.objects.prefetch_related("role").annotate(number_of_staff = Count("role"))
    serializer_class = RoleSerializer
    permission_classes = [StatistikaPermission]
    