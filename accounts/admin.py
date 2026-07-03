from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username", "email", "interface_language",
        "current_streak_days", "longest_streak_days", "is_staff",
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        ("SuperTutor ma'lumotlari", {
            "fields": (
                "interface_language", "avatar", "bio", "date_of_birth",
                "current_streak_days", "longest_streak_days", "last_activity_date",
            )
        }),
    )
