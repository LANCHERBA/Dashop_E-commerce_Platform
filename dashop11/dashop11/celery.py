from celery import  Celery
import os
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE','dashop11.settings')

app = Celery('dashop11')

app.conf.update(
    BROKER_URL = 'redis://@127.0.0.1:6379/4'
)

app.autodiscover_tasks(settings.INSTALLED_APPS)
