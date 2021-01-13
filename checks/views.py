import os
import time

from django.db import connections
from django.db.utils import OperationalError
from django.http import HttpResponse
from django.shortcuts import render

from redis import Redis
import kafka

from devops_001.celery import app as celery_app


def index(request):
    context = {
        'nginx': _check_nginx_connection(request),
        'database': _check_database_connection(),
        'redis': _check_redis_connection(),
        'celery': _check_celery_connection(),
        'kafka': _check_kafka_connection()
    }
    return render(request, 'checks/index.html', context)


def _check_nginx_connection(request):
    return 'HTTP_USING_NGINX' in request.META


def _check_redis_connection():
    try:
        redis_host = os.environ.get('REDIS_HOST', '')

        redis_client = Redis(redis_host, socket_connect_timeout=1)
        redis_client.ping()
    except Exception:
        return False

    return True


def _check_celery_connection():
    celery_response = celery_app.control.inspect().ping()
    return celery_response is not None


def _check_database_connection():
    try:
        connections['default'].cursor()
    except OperationalError:
        return False

    return True


def _check_kafka_connection():
    try:
        server = os.environ.get('KAFKA_HOST', '') + ':' + os.environ.get('KAFKA_PORT', '')
        producer = kafka.KafkaProducer(bootstrap_servers=server)

        for _ in range(100):
            producer.send('foobar', b'some_message_bytes')

        return True
    except Exception as e:
        return False
