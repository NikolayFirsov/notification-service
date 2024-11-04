# tasks.py
import logging
from celery import shared_task, current_app
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .models import Mailing, Message

logger = logging.getLogger('notification_service')


@shared_task
def send_messages(mailing_id):
    """
    Функция для рассылки сообщений.
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        messages = Message.objects.filter(mailing=mailing, is_sending=False)
        logger.info(f'Начало рассылки с ID {mailing_id}')
        for message in messages:
            logger.info(f'Текст: "{mailing.message_text}"')
            message.is_sending = True
            message.sending_at = timezone.now()
            message.save()
    except ObjectDoesNotExist:
        logger.info(f'Рассылка с ID {mailing_id} не найдена')


def revoke_task(task_id):
    """
    Отменяет запланированную задачу в Celery.
    """
    current_app.control.revoke(task_id, terminate=True)
