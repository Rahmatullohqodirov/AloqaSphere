import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
app = Celery('AloqaSphere')

app.config_from_object('django.conf:settigs', namespace='CELERY')
app.autodiscover_tasks()