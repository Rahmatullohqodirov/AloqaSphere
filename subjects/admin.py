from django.contrib import admin

from .models import Subject, SubjectLevel


class SubjectLevelInline(admin.TabularInline):
    model = SubjectLevel
    extra = 1


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("display_name", "code", "is_language", "is_active")
    inlines = [SubjectLevelInline]
