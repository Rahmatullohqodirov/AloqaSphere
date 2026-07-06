import logging
from celery import shared_task
from django.core.mail import send_mail
from decouple import config
logger = logging.getLogger(__name__)
@shared_task
def send_verification_code(email, code):
    try:
        is_send = send_mail(
            subject="AloqaSphere",
            message=f"Sizning registrasiya kodingiz {code}",
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[email],
        )
        return is_send
    
    except Exception as e:
        logger.error(f"Xatolik {email}:{e}")
        return 0