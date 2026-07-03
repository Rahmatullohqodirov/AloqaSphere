from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class InterfaceLanguage(models.TextChoices):
        UZBEK = "uz", "O'zbek"
        RUSSIAN = "ru", "Rus"
        ENGLISH = "en", "Ingliz"
        TURKISH = "tr", "Turk"

    interface_language = models.CharField(
        max_length=5,
        choices=InterfaceLanguage.choices,
        default=InterfaceLanguage.UZBEK,
        help_text="Ilova interfeysi tili",
    )
    avatar = models.ImageField(upload_to="user_avatars/", blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)

    current_streak_days = models.PositiveIntegerField(default=0)
    longest_streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
