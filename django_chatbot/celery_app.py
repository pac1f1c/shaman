from celery import Celery
from django.conf import settings

app = Celery('django_chatbot',
             broker=settings.DJANGO_CHATBOT['BROKER'],
             include='django_chatbot.tasks')





app.config_from_object('django.conf:settings', namespace='CELERY')
