from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class LearningSession(models.Model):


    class SessionType(models.TextChoices):
        CONVERSATION = "conversation", "Suhbat (Immersion)"
        GRAMMAR = "grammar", "Grammatika mashqi"
        VOCABULARY = "vocabulary", "Lug'at / Flashcards"
        ROLEPLAY = "roleplay", "Role-play"
        MATH_PROBLEM = "math_problem", "Matematika masalasi"
        QUIZ = "quiz", "Quiz"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions"
    )
    subject = models.ForeignKey(
        "subjects.Subject", on_delete=models.CASCADE, related_name="sessions"
    )
    session_type = models.CharField(max_length=20, choices=SessionType.choices)

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(
        help_text="Sessiya davomiyligi (daqiqa)"
    )

    pronunciation_accuracy = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Talaffuz aniqligi foizi (0-100)",
    )
    grammar_accuracy = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Grammatika aniqligi foizi (0-100)",
    )
    level_at_session = models.CharField(
        max_length=20, blank=True, help_text="Sessiya vaqtidagi daraja, masalan A2"
    )

    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)

    notes = models.TextField(blank=True, help_text="AI Feedback Agent xulosasi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "subject", "started_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.subject.code} - {self.started_at:%Y-%m-%d}"

    @property
    def accuracy_percent(self):
        if self.total_questions == 0:
            return None
        return round((self.correct_answers / self.total_questions) * 100, 1)


class UserSubjectProgress(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subject_progress"
    )
    subject = models.ForeignKey(
        "subjects.Subject", on_delete=models.CASCADE, related_name="user_progress"
    )

    total_minutes = models.PositiveIntegerField(default=0)
    sessions_count = models.PositiveIntegerField(default=0)
    current_level = models.CharField(max_length=20, blank=True)

    average_pronunciation = models.FloatField(null=True, blank=True)
    average_grammar = models.FloatField(null=True, blank=True)

    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "subject")

    def __str__(self):
        return f"{self.user} - {self.subject.code} progress"

    @property
    def average_session_length(self):
        if self.sessions_count == 0:
            return 0
        return round(self.total_minutes / self.sessions_count, 1)

    @property
    def correct_answer_rate(self):
        if self.total_questions == 0:
            return None
        return round((self.correct_answers / self.total_questions) * 100, 1)


class DailyActivity(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_activities"
    )
    date = models.DateField()
    minutes_spent = models.PositiveIntegerField(default=0)
    sessions_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user} - {self.date}"
