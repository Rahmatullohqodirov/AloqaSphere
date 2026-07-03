from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from learning.models import LearningSession, UserSubjectProgress, DailyActivity
from learning.serializers import UserSubjectProgressSerializer, DailyActivitySerializer

User = get_user_model()


class DashboardView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        progress_qs = UserSubjectProgress.objects.filter(user=user).select_related("subject")

        totals = progress_qs.aggregate(
            total_minutes=Sum("total_minutes"),
            total_sessions=Sum("sessions_count"),
        )

        data = {
            "total_hours": round((totals["total_minutes"] or 0) / 60, 1),
            "total_sessions": totals["total_sessions"] or 0,
            "current_streak_days": user.current_streak_days,
            "longest_streak_days": user.longest_streak_days,
            "subjects": UserSubjectProgressSerializer(progress_qs, many=True).data,
        }
        return Response(data)


class HeatmapView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get("days", 90))
        since = timezone.now().date() - timedelta(days=days)
        activities = DailyActivity.objects.filter(
            user=request.user, date__gte=since
        ).order_by("date")
        return Response(DailyActivitySerializer(activities, many=True).data)


class WeeklyReportView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        this_week_start = today - timedelta(days=6)
        last_week_start = today - timedelta(days=13)
        last_week_end = today - timedelta(days=7)

        this_week = DailyActivity.objects.filter(
            user=user, date__gte=this_week_start, date__lte=today
        ).aggregate(minutes=Sum("minutes_spent"), sessions=Sum("sessions_count"))

        last_week = DailyActivity.objects.filter(
            user=user, date__gte=last_week_start, date__lte=last_week_end
        ).aggregate(minutes=Sum("minutes_spent"), sessions=Sum("sessions_count"))

        this_minutes = this_week["minutes"] or 0
        last_minutes = last_week["minutes"] or 0

        if last_minutes == 0:
            growth_percent = 100.0 if this_minutes > 0 else 0.0
        else:
            growth_percent = round(((this_minutes - last_minutes) / last_minutes) * 100, 1)

        return Response({
            "period": {"from": this_week_start, "to": today},
            "this_week_minutes": this_minutes,
            "this_week_sessions": this_week["sessions"] or 0,
            "last_week_minutes": last_minutes,
            "growth_percent": growth_percent,
        })


class LeaderboardView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subject_code = request.query_params.get("subject")
        qs = UserSubjectProgress.objects.all()
        if subject_code:
            qs = qs.filter(subject__code=subject_code)

        qs = qs.order_by("-total_minutes")[:20]

        results = []
        my_position = None
        for i, entry in enumerate(qs, start=1):
            is_me = entry.user_id == request.user.id
            if is_me:
                my_position = i
            results.append({
                "position": i,
                "is_you": is_me,
                "display_name": "Siz" if is_me else f"Foydalanuvchi #{entry.user_id}",
                "total_minutes": entry.total_minutes,
                "current_level": entry.current_level,
            })

        return Response({"leaderboard": results, "your_position": my_position})