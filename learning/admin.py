from django.contrib import admin

from .models import LearningSession, UserSubjectProgress, DailyActivity


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user", "subject", "session_type", "started_at",
        "duration_minutes", "level_at_session",
    )
    list_filter = ("subject", "session_type")
    search_fields = ("user__username",)


@admin.register(UserSubjectProgress)
class UserSubjectProgressAdmin(admin.ModelAdmin):
    list_display = (
        "user", "subject", "total_minutes", "sessions_count",
        "current_level", "average_pronunciation", "average_grammar",
    )
    list_filter = ("subject",)


@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "minutes_spent", "sessions_count")
    list_filter = ("date",)
