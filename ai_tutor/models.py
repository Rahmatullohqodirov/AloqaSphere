from django.conf import settings
from django.db import models


class Conversation(models.Model):

    class SessionType(models.TextChoices):
        CONVERSATION = "conversation", "Suhbat (Immersion)"
        GRAMMAR = "grammar", "Grammatika mashqi"
        ROLEPLAY = "roleplay", "Role-play"
        MATH_PROBLEM = "math_problem", "Matematika masalasi"
        QUIZ = "quiz", "Quiz"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_conversations"
    )
    subject = models.ForeignKey(
        "subjects.Subject", on_delete=models.CASCADE, related_name="ai_conversations"
    )
    session_type = models.CharField(
        max_length=20, choices=SessionType.choices, default=SessionType.CONVERSATION
    )
    target_level = models.CharField(
        max_length=20, blank=True,
        help_text="Suhbat boshlanishidagi daraja, masalan A2 (bo'sh bo'lsa AI avtomatik moslaydi)",
    )

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    grammar_accuracy = models.FloatField(null=True, blank=True)
    suggested_level = models.CharField(max_length=20, blank=True)
    summary_notes = models.TextField(blank=True)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)

    learning_session = models.OneToOneField(
        "learning.LearningSession", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="ai_conversation",
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} - {self.subject.code} - {self.started_at:%Y-%m-%d %H:%M}"


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Foydalanuvchi"
        ASSISTANT = "assistant", "AI"
        SYSTEM = "system", "Tizim"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:40]}"
