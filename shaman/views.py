""" This module contains views."""

import json
import logging

from django.http import JsonResponse, HttpRequest
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from shaman.tasks import dispatch

log = logging.getLogger(__name__)


@csrf_exempt
@never_cache
def webhook(request: HttpRequest, token_slug) -> JsonResponse:
    """ Telegram webhook.

    This view asynchronously calls dispatch task that handles incoming
    telegram updates.

    Args:
        request: Telegram update request.
        token_slug: Bot token slug.

    Returns:
        JsonResponse to Telegram.

    """
    update_data = json.loads(request.body)
    dispatch.delay(update_data=update_data, token_slug=token_slug)
    log.debug("Request %s slug_token %s", update_data, token_slug)
    return JsonResponse({"ok": "POST request processed"})
