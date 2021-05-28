""" This module contains class dispatching incoming Telegram updates"""

import importlib
import logging
from functools import lru_cache
from typing import Dict, Iterable, List

from django.conf import settings

from shaman.models import Bot, Form, Update
from shaman.handlers import Handler
from shaman.telegram.types import Update as TelegramUpdate

log = logging.getLogger(__name__)


@lru_cache(maxsize=settings.shaman.get('LOAD_HANDLERS_CACHE_SIZE'))
def load_handlers() -> Dict[str, List[Handler]]:
    """Load registered handlers for all bots

    Returns:
        dictionary like
        {'first_bot_token':[Handler_1, Handler_2 ... ]

    """
    handlers = {}
    for bot in Bot.objects.all():
        handlers[bot.token_slug] = _load_bot_handlers(bot.root_handlerconf)
        log.info(
            "Handlers %s for bot %s has been loaded",
            bot.root_handlerconf,
            bot.name,
        )
    return handlers


def _load_bot_handlers(module_name: str) -> List[Handler]:
    """Return handler for a bot.

    shaman loads the module and looks for the variable `handlers`.
    This should be a list of `Handler` instances.

    Args:
        module_name: Full module name where to search handlers.

    Returns:
        list of `Handler`

    """
    module = importlib.import_module(module_name)
    return module.handlers  # noqa


class Dispatcher:
    """This class dispatches incoming Telegram updates.

    Dispatcher iterates all registered handlers until the handler matches
    the update. Then Dispatcher calls the handler `handle_update` method.

    Note: To register handlers for a bot, add some module that contains
        the `handlers` variable. This should be a list of `Handler` instances.
        Then add the module name to bot 'ROOT_HANDLERCONF' setting.

    Args:
        update_data: The incoming update dictionary.
        token_slug: The bot token slug.

    Attributes:
        bot (Bot): The bot model.
        update (Update): The update object.
        handlers: List of handler registered to this bot.

    """

    def __init__(self, token_slug: str):
        self.bot = Bot.objects.get(token_slug=token_slug)
        self.handlers = load_handlers()[self.bot.token_slug]

    def dispatch(self, update_data: dict):
        """Dispatch incoming Telegram updates"""
        update = Update.objects.from_telegram(
            bot=self.bot, telegram_update=TelegramUpdate.from_dict(update_data)
        )
        if form_keeper := Form.objects.get_form(update):
            if not self._check_handlers(
                update=update,
                handlers=[h for h in self.handlers if h.suppress_form]
            ):
                form_keeper.form.update(update=update)
        else:
            self._check_handlers(update, self.handlers)

    @staticmethod
    def _check_handlers(update: Update,
                        handlers: Iterable[Handler]) -> bool:
        """Check if one of the handlers match the update

        Args:
            update: The update to check.
            handlers: The handlers to check.

        Returns:
            True if one of the handlers match the update.

        """
        for handler in handlers:
            if handler.match(update=update):
                handler.handle_update(update=update)
                return True
        return False
