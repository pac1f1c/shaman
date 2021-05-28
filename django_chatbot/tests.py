from __future__ import annotations

import logging
import re
from typing import List, Optional, Union
from unittest.mock import patch

from django.db.models import QuerySet
from django.forms import Form
from django.test import TestCase as DjangoTestCase
from django.utils import timezone

from shaman.models import Bot, CallbackQuery, Chat, Message, Update, \
    User
from shaman.services.dispatcher import Dispatcher
from shaman.telegram import types

START_USER_ID = 1000

log = logging.getLogger(__name__)


class MockUserError(Exception):
    pass


class MockUser:
    def __init__(self,
                 bot: Bot,
                 username: str = None):
        self.bot = bot
        self.user_id = self._next_user_id()
        if username is None:
            username = f'test_user_{self.user_id}'
        self.username = username
        self.user = User.objects.create(
            user_id=self.user_id, is_bot=False, username=username,
            first_name=username, last_name=username
        )
        self.chat = Chat.objects.create(
            bot=self.bot, chat_id=self.user_id, type='private',
            username=username, first_name=username, last_name=username
        )
        self.dispatcher = Dispatcher(bot.token_slug)

    def _next_user_id(self) -> int:
        users = User.objects.all().order_by('user_id')
        last = users.last()
        if last:
            return last.user_id + 1
        else:
            return START_USER_ID

    def messages(self) -> QuerySet[Message]:
        """Return `Message` query set related to the user"""
        messages = Message.objects.filter(
            chat=self.chat
        ).order_by('-message_id')
        return messages

    def updates(self) -> QuerySet[Update]:
        """Return `Update` query set related to the user"""
        updates = Update.objects.filter(
            message__chat=self.chat
        ).order_by('-update_id')
        return updates

    def callback_queries(self) -> QuerySet[CallbackQuery]:
        """Return `Update` query set related to the user"""
        callback_queries = CallbackQuery.objects.filter(
            from_user=self.user
        ).order_by('-callback_query_id')
        return callback_queries

    def form(self) -> Optional[Form]:
        if last := self.chat.messages.last():
            if form_model := last.form:
                return form_model.form

    def _next_message_id(self) -> int:
        messages = Message.objects.filter(
            chat__chat_id=self.user_id
        ).order_by('message_id')
        last = messages.last()
        if last:
            return last.message_id + 1
        else:
            return 1

    def _next_callback_query_id(self) -> str:
        callbacks = CallbackQuery.objects.all()
        last = callbacks.last()
        if last:
            return str(int(last.callback_query_id) + 1)
        else:
            return "1"

    def _next_update_id(self) -> int:
        last = Update.objects.all().order_by('update_id').last()
        if last:
            return last.update_id + 1
        else:
            return 1

    def _telegram_user(self):
        user = types.User(
            id=self.user_id,
            is_bot=False,
            username=self.username,
            first_name=self.username,
            last_name=self.username,
        )
        return user

    def _telegram_chat(self):
        user = types.Chat(
            id=self.user_id,
            type='private',
            username=self.username,
            first_name=self.username,
            last_name=self.username,
        )
        return user

    @staticmethod
    def _extract_entities(text: str):
        pattern = re.compile(r'/\w+')
        entities = []
        for match in re.finditer(pattern, text):
            offset, end = match.span()
            length = end - offset
            entities.append(
                {'offset': offset, 'length': length, 'type': 'bot_command'}
            )
        if entities:
            return entities

    def send_message(self, message_text: str):
        """Simulate sending message to bot by the user."""
        message = types.Message(
            message_id=self._next_message_id(),
            date=timezone.now(),
            chat=self._telegram_chat(),
            from_user=self._telegram_user(),
            text=message_text,
            entities=self._extract_entities(message_text),
        )
        update = types.Update(
            update_id=self._next_update_id(),
            message=message,
        )
        self.dispatcher.dispatch(
            update_data=update.to_dict(date_as_timestamp=True)
        )

    def send_callback_query(self, data: str, markup_message: Message = None):
        if markup_message is None:
            last = self.messages().first()
            if last is None or last.reply_markup is None:
                raise ValueError("No ReplyMarkup to response")
            else:
                markup_message = last
        callback_query = types.CallbackQuery(
            id=self._next_callback_query_id(),
            from_user=self._telegram_user(),
            chat_instance=self._next_callback_query_id(),
            message=types.Message(
                message_id=markup_message.message_id,
                chat=self._telegram_chat(),
                date=markup_message.date,
            ),
            data=data,
        )
        update = types.Update(
            update_id=self._next_update_id(),
            callback_query=callback_query,
        )
        self.dispatcher.dispatch(
            update_data=update.to_dict(date_as_timestamp=True)
        )


class MockShaman:
    def __init__(self):
        self.sent_messages = []

    def last_message(self):
        if self.sent_messages:
            return self.sent_messages[-1]

    def send_message_patch(self,
                           chat_id: int,
                           text: str,
                           parse_mode: str = None,
                           entities: List[types.MessageEntity] = None,
                           disable_web_page_preview: bool = False,
                           disable_notification: bool = False,
                           reply_to_message_id: int = None,
                           allow_sending_without_reply: bool = True,
                           reply_markup: Union[
                               types.ForceReply,
                               types.InlineKeyboardMarkup,
                               types.ReplyKeyboardMarkup,
                               types.ReplyKeyboardRemove,
                           ] = None
                           ) -> types.Message:
        """Use this method to send text messages.
        """
        log.warning("Normal responce")
        params = {
            'chat_id': chat_id,
            'text': text,
            'entities': entities,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'allow_sending_without_reply': allow_sending_without_reply,
            'reply_markup': reply_markup,
        }
        self.sent_messages.append(params)
        last_message = Message.objects.order_by('-message_id').first()
        user = types.User(id=1, is_bot=True, username="Bot")
        telegram_chat = types.Chat(id=chat_id, type="private")
        message = types.Message(
            message_id=last_message.message_id + 1,
            date=timezone.now(),
            chat=telegram_chat,
            from_user=user,
            text=text,
            entities=entities,
            reply_markup=reply_markup,
        )
        return message


class TestCase(DjangoTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.mock_Shaman = MockShaman()
        self.send_message_patcher = patch(
            "shaman.telegram.api.Api.send_message",
            side_effect=self.mock_Shaman.send_message_patch
        )
        self.send_message_patcher.start()

    def tearDown(self) -> None:
        self.send_message_patcher.stop()
        super().tearDown()
