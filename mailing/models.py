from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class Mailing(models.Model):
    """
    Модель для хранения информации о рассылках.

     Атрибуты:
        start_time (DateTime): Дата и время запуска рассылки;
        end_time (DateTime): Дата и время окончания рассылки;
        message_text (Str): Текст сообщения для доставки клиенту;
        mobile_operator_code (Str): Код мобильного оператора клиентов;
        tag (Str): Тег клиентов;
        task_id (Str): ID задачи Celery.
    """
    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    start_time = models.DateTimeField(verbose_name='Дата и время запуска рассылки')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания рассылки')
    message_text = models.TextField(verbose_name='Текст сообщения для доставки клиенту')
    mobile_operator_code = models.CharField(verbose_name='Фильтр по коду мобильного оператора клиента', max_length=3)
    tag = models.CharField(verbose_name='Фильтр по тегу клиента', max_length=50)
    task_id = models.CharField(verbose_name='ID задачи Celery', max_length=50, blank=True, null=True)

    def __str__(self):
        return f'Рассылка {self.pk}'

    def clean(self):
        if self.start_time > self.end_time:
            raise ValidationError('Дата и время начала не может превышать значение даты и времени окончания рассылки')


class Client(models.Model):
    """
    Модель для хранения информации о клиентах.

    Атрибуты:
        phone_number (Str): Дата и время запуска рассылки (формат 7XXXXXXXXXX, X - цифра);
        mobile_operator_code (Str): Код мобильного оператора клиента (три цифры);
        tag (Str): Тег клиента.
    """
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    phone_validator = RegexValidator(
        regex=r'^7\d{10}$',
        message='Неверный формат номер телефона, используйте такой формат: 7XXXXXXXXXX (X - цифра от 0 до 9)'
    )
    operator_code_validator = RegexValidator(
        regex=r'^\d{3}$',
        message='Код мобильного оператора должен состоять из трех цифр'
    )

    phone_number = models.CharField(
        verbose_name='Номер телефона клиента',
        help_text='Необходимо ввести в формате: 7XXXXXXXXXX (X - цифра от 0 до 9)',
        max_length=11,
        unique=True,
        validators=[phone_validator]
    )
    mobile_operator_code = models.CharField(
        verbose_name='Код мобильного оператора',
        help_text='Должен состоять из трех цифр',
        max_length=3,
        validators=[operator_code_validator]
    )
    tag = models.CharField(verbose_name='Тег (произвольная метка)', max_length=50)

    def __str__(self):
        return f'Клиент {self.pk} - {self.phone_number}'


class Message(models.Model):
    """
    Модель для хранения информации о сообщениях.

    Атрибуты:
        created_at (DateTime): Дата и время создания;
        sending_at (DateTime): Дата и время отправки;
        mailing (FK): Рассылка;
        client (FK): Клиент;
        is_sending (Bool): Отправлено ли сообщение.
    """
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    created_at = models.DateTimeField(verbose_name='Дата и время создания', auto_now_add=True)
    sending_at = models.DateTimeField(verbose_name='Дата и время отправки', null=True, blank=True)
    mailing = models.ForeignKey(Mailing, verbose_name='Рассылка', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, verbose_name='Клиент', on_delete=models.CASCADE)
    is_sending = models.BooleanField(verbose_name='Сообщение отправлено', default=False)

    def __str__(self):
        return f'Сообщение {self.pk} Клиенту {self.client}'

