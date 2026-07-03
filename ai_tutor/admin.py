from django.contrib import admin

from .models import Conversation, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("role", "content", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "user", "subject", "session_type", "started_at", "ended_at",
        "is_active", "grammar_accuracy", "suggested_level",
    )
    list_filter = ("subject", "session_type", "is_active")
    search_fields = ("user__username",)
    inlines = [ChatMessageInline]
