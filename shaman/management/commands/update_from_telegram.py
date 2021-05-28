from django.core.management import BaseCommand

from shaman.models import Bot
from telegram.api import TelegramError


class Command(BaseCommand):
    def handle(self, *args, **options):
        for bot in Bot.objects.all():
            try:
                bot.get_me()
            except TelegramError as error:
                print(f"Exception during updating bot info.\n{error}")
                continue
            else:
                print(f"Bot info was updated from telegram for {bot.name}.")
            try:
                bot.get_webhook_info()
            except TelegramError as error:
                print(f"Exception during updating bot webhook info.\n{error}")
                continue
            else:
                print(f"Bot webhook info was updated from telegram for {bot.name}.") # noqa
