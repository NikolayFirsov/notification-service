from rest_framework import serializers
from .models import Mailing, Client, Message


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = ('start_time', 'end_time', 'message_text', 'mobile_operator_code', 'tag')

    def validate(self, attrs):
        """
        Проверяем, что start_time меньше или равен end_time
        """
        if attrs.get('start_time') > attrs.get('end_time'):
            raise serializers.ValidationError({
                'date_error': 'Дата и время начала не может превышать значение даты и времени окончания рассылки'
            })
        return attrs


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
