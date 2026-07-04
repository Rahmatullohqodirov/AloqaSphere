from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def notification_admin(report_title, report_description, user_username):
    subject = f"Yangi Report keldi {report_title}"
    message = f"yuboruvchi: {user_username}\nMavzu: {report_title}\nTavsif:\n{report_description}"
    from_email = settings.DJANGO_FROM_EMAIL
    recipient_list = [admin[1] for admin in settings.ADMINS]

    send_mail(subject, message, from_email, recipient_list)
    return "Adminga xat yuborildi"