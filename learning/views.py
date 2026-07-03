from rest_framework import viewsets, permissions

from .models import LearningSession, UserSubjectProgress
from .serializers import LearningSessionSerializer, UserSubjectProgressSerializer


class LearningSessionViewSet(viewsets.ModelViewSet):

    serializer_class = LearningSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = LearningSession.objects.filter(user=self.request.user).select_related("subject")
        subject_id = self.request.query_params.get("subject")
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs


class UserSubjectProgressViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = UserSubjectProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSubjectProgress.objects.filter(
            user=self.request.user
        ).select_related("subject")