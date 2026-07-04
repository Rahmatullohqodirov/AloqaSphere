from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from user.models import Role
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RoleSerializer, ReportSerializer
from django.db.models import Count
from .permissions import StatistikaPermission
from .tasks import notification_admin

class RoleByUserView(generics.ListAPIView):
    queryset = Role.objects.prefetch_related("role").annotate(number_of_staff = Count("role"))
    serializer_class = RoleSerializer
    permission_classes = [StatistikaPermission]

class ReportView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({
                "detail": "error",
                "error": serializer.errors
            }, status=400)
        report=serializer.save(reported=request.user)

        notification_admin.delay(
            report_title=report.title,
            report_description=report.description,
            user_username=request.reporter.username
        )
        return Response({
            "detail": "Succesfully reported"
        }, status=200)