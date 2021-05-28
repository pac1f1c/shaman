from celery import Celery
from django.conf import settings

app = Celery('shaman',
             broker=settings.shaman['BROKER'],
             include='shaman.tasks')





app.config_from_object('django.conf:settings', namespace='CELERY')
