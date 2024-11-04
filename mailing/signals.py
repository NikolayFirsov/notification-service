import logging

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import Mailing, Client, Message
from .tasks import send_messages, revoke_task

logger = logging.getLogger('notification_service')


def create_or_update_messages(mailing: Mailing, is_update: bool) -> None:
    """
    Функция для создания или обновления сообщений (Message) по созданной или измененной рассылке.
    """
    if is_update:
        Message.objects.filter(mailing=mailing).delete()
    clients = Client.objects.filter(
        mobile_operator_code=mailing.mobile_operator_code,
        tag=mailing.tag
    )
    messages = [Message(mailing=mailing, client=client) for client in clients]
    Message.objects.bulk_create(messages)
    if is_update:
        logger.info(f'Для рассылки "{mailing}" было обновлено {len(messages)} сообщений')
    else:
        logger.info(f'Создано {len(messages)} сообщений для рассылки "{mailing}"')


def start_or_planning_mailing(mailing: Mailing) -> None | int:
    """
    Функция для запуска или планирования созданной рассылки.
    Если текущее время в диапазоне для рассылки, то рассылка запускается.
    Если текущее время меньше начала рассылки, то рассылка планируется на время начала диапазона.
    Если текущее время больше времени окончания рассылки, то is_sending ("Отправлено") у сообщений остаются в False.
    Возвращает ID задачи Celery или None если задача не была создана.
    """
    local_now = timezone.localtime(timezone.now())

    task_id = None
    if mailing.start_time <= local_now <= mailing.end_time:
        task_id = send_messages.delay(mailing.pk).id
        logger.info(f'Рассылка "{mailing}" будет запущена немедленно.')
    elif mailing.start_time > local_now:
        task_id = send_messages.apply_async((mailing.pk,), eta=mailing.start_time).id
        logger.info(f'Рассылка "{mailing}" запланирована на {mailing.start_time}.')
    return task_id


@receiver(pre_save, sender=Mailing, dispatch_uid='check_and_revoke_old_task')
def check_and_revoke_old_task(sender, instance, update_fields, **kwargs):
    """
    Функция для внесения изменений при редактировании объекта Mailing.
    Отмена старой и создания новой задачи Celery, пересоздание сообщений (Message).
    """
    if old_instance := Mailing.objects.filter(pk=instance.pk).first():
        significant_changes = any([
            old_instance.start_time != instance.start_time,
            old_instance.end_time != instance.end_time,
            old_instance.tag != instance.tag,
            old_instance.mobile_operator_code != instance.mobile_operator_code
        ])
        if significant_changes:
            revoke_task(old_instance.task_id)
            create_or_update_messages(instance, True)
            logger.info(f'Старая задача {old_instance.task_id} для рассылки "{old_instance}" отменена.')
            instance.task_id = start_or_planning_mailing(instance)


@receiver(post_save, sender=Mailing, dispatch_uid='create_message')
def create_message(sender, instance, created, **kwargs):
    """
    Функция для создания сообщений (Message) и задачи Celery при создании объекта Mailing.
    """
    if created:
        create_or_update_messages(instance, False)
        task_id = start_or_planning_mailing(instance)
        Mailing.objects.filter(pk=instance.pk).update(task_id=task_id)


@receiver(post_delete, sender=Mailing, dispatch_uid='delete_mailing_task')
def delete_mailing_task(sender, instance, **kwargs):
    """
    Функция для отмены задачи Celery при удалении объекта Mailing.
    """
    # Проверяем, если у рассылки есть идентификатор задачи
    if instance.task_id:
        # Отменяем задачу по её ID
        revoke_task(instance.task_id)
        logger.info(f'Задача с ID {instance.task_id} отменена, поскольку рассылка "{instance}" была удалена.')
