from django.contrib import admin

from mailing.models import Mailing, Client, Message


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """
    Админка для Mailing.
    """
    list_display = ('id', 'start_time', 'end_time', 'mobile_operator_code', 'tag')
    list_display_links = ('id', 'start_time', 'end_time')
    search_fields = ('id', 'mobile_operator_code', 'tag', 'message_text')
    list_filter = ('mobile_operator_code', 'tag')
    readonly_fields = ('task_id', )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Админка для Client.
    """
    list_display = ('id', 'phone_number', 'mobile_operator_code', 'tag')
    list_display_links = ('id', 'phone_number')
    search_fields = ('id', 'phone_number', 'mobile_operator_code', 'tag')
    list_filter = ('mobile_operator_code', 'tag')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Админка для Message.
    """
    list_display = ('id', 'mailing', 'client', 'created_at', 'sending_at', 'is_sending')
    list_display_links = ('id', 'mailing')
    search_fields = ('id', )
    readonly_fields = ('is_sending', 'created_at', 'sending_at')
