from django.contrib import admin
from django.db.models import F

from .models import Bot, CallbackQuery, Chat, Form, Message, Update, User


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "update_successful",
        "me_update_datetime",
        "webhook_update_datetime",
    ]


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = [
        "bot",
        "chat_id",
        "type",
        "username"
    ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "bot_name",
        "direction",
        "message_id",
        "date",
        "chat",
        "trancated_text",
    ]

    def get_queryset(self, request):
        query_set = super().get_queryset(request)
        query_set = query_set.annotate(bot_name=F('chat__bot__name'))
        return query_set

    def trancated_text(self, obj):
        return obj.text[:20]

    def bot_name(self, obj):
        return obj.bot_name

    bot_name.admin_order_field = 'bot_name'


@admin.register(CallbackQuery)
class CallbackQueryAdmin(admin.ModelAdmin):
    list_display = [
       "callback_query_id",
       "from_user",
    ]


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = [
        "bot",
        "update_id",
        "handler",
        "type",
    ]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "user_id",
        "username",
    ]


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [
        "id",
    ]
