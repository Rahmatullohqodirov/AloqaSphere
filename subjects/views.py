from rest_framework import viewsets, permissions

from .models import Subject
from .serializers import SubjectSerializer


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Subject.objects.filter(is_active=True).prefetch_related("levels")
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
