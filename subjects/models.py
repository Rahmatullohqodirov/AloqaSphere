from django.db import models


class Subject(models.Model):


    class Code(models.TextChoices):
        ENGLISH = "english", "Ingliz tili"
        RUSSIAN = "russian", "Rus tili"
        GERMAN = "german", "Nemis tili"
        TURKISH = "turkish", "Turk tili"
        MATH = "math", "Matematika"

    code = models.CharField(max_length=20, choices=Code.choices, unique=True)
    display_name = models.CharField(max_length=100)
    is_language = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Frontend uchun ikonka nomi")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class SubjectLevel(models.Model):

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="levels")
    code = models.CharField(max_length=20)  # masalan: A1, A2, B1... yoki Beginner
    order = models.PositiveSmallIntegerField(help_text="Daraja tartibi, kichikdan kattaga")

    class Meta:
        ordering = ["subject", "order"]
        unique_together = ("subject", "code")

    def __str__(self):
        return f"{self.subject.code} - {self.code}"
