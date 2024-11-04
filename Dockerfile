FROM python:3.12

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE notification_service.settings  # Используем ваш модуль настроек
