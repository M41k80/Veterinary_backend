import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veterinary_backend.settings')

app = Celery('veterinary_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
