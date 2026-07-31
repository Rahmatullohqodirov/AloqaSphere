from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

@shared_task
def send_verification_code(email, code):
    subject = "Tasdiqlash kodi"
    message = f"Sizning tasdiqlash kodingiz: {code}"
    from_email = settings.EMAIL_HOST_USER 
    send_mail(subject, message, from_email, [email])