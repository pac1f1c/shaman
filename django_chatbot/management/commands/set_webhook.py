from django.core.management import BaseCommand

from django_chatbot.models import Bot
from telegram.api import TelegramError


class Command(BaseCommand):
    def handle(self, *args, **options):
        for bot in Bot.objects.all():
            try:
                bot.set_webhook()
            except TelegramError as error:
                print(f"Exception during setWebhook \n{error}")
                continue
            else:
                print(f"Webhook was successfully set for {bot.name}.")
            try:
                bot.get_webhook_info()
            except TelegramError as error:
                print(f"Exception during getWebhookInfo \n{error}")
            else:
                print(f"Webhook was successfully updated for {bot.name}.")
