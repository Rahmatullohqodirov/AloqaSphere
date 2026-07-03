from django.core.management.base import BaseCommand

from subjects.models import Subject, SubjectLevel

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
MATH_LEVELS = ["Beginner", "Elementary", "Intermediate", "Advanced"]

SUBJECTS = [
    {"code": Subject.Code.ENGLISH, "display_name": "Ingliz tili", "is_language": True, "icon": "flag-uk", "levels": CEFR_LEVELS},
    {"code": Subject.Code.RUSSIAN, "display_name": "Rus tili", "is_language": True, "icon": "flag-ru", "levels": CEFR_LEVELS},
    {"code": Subject.Code.GERMAN, "display_name": "Nemis tili", "is_language": True, "icon": "flag-de", "levels": CEFR_LEVELS},
    {"code": Subject.Code.TURKISH, "display_name": "Turk tili", "is_language": True, "icon": "flag-tr", "levels": CEFR_LEVELS},
    {"code": Subject.Code.MATH, "display_name": "Matematika", "is_language": False, "icon": "calculator", "levels": MATH_LEVELS},
]


class Command(BaseCommand):
    help = "TZ dagi 5 ta fanni (Ingliz, Rus, Nemis, Turk, Matematika) va ularning darajalarini yuklaydi."

    def handle(self, *args, **options):
        for item in SUBJECTS:
            subject, created = Subject.objects.update_or_create(
                code=item["code"],
                defaults={
                    "display_name": item["display_name"],
                    "is_language": item["is_language"],
                    "icon": item["icon"],
                },
            )
            for order, level_code in enumerate(item["levels"], start=1):
                SubjectLevel.objects.update_or_create(
                    subject=subject, code=level_code, defaults={"order": order}
                )
            status = "yaratildi" if created else "yangilandi"
            self.stdout.write(self.style.SUCCESS(f"{subject.display_name} - {status}"))

        self.stdout.write(self.style.SUCCESS("Barcha fanlar muvaffaqiyatli yuklandi."))
