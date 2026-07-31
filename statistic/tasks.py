from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(name='statistic.tasks.notification_admin')
def notification_admin(report_title, report_description, user_fullname):
    subject = f"Yangi Report keldi {report_title}"
    message = f"yuboruvchi: {user_fullname}\nMavzu: {report_title}\nTavsif:\n{report_description}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['javohirboboxonov08@gmail.com']   

    send_mail(subject, message, from_email, recipient_list)
    return "Adminga xat yuborildi"