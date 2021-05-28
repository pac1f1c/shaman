"""This module contains all Celery tasks"""

import logging

from celery import Task
from celery import shared_task

from django_chatbot.services.dispatcher import Dispatcher

log = logging.getLogger(__name__)


class LoggingTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        log.exception(
            "Task %s (id=%s) failed, exc=%s  exinfo=%s",
            self.name, task_id, exc, einfo
        )
        super(LoggingTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@shared_task(bind=True, ignore_result=True, base=LoggingTask)
def dispatch(self, update_data: dict, token_slug: str):
    """This tasks dispatches incoming telegram update.

    Args:
        update_data: The incoming update dictionary.
        token_slug: The bot token slug.

    """
    log.debug(
        "dispatch task update_data=%s token_slug=%s", update_data, token_slug
    )
    dispatcher = Dispatcher(token_slug=token_slug)
    dispatcher.dispatch(update_data=update_data)
