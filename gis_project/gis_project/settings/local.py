from gis_project.settings.base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'gis_user123',
        'HOST': 'db',
        'PORT': '5432',
    },
}
CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672/'
CELERY_RESULT_BACKEND = 'redis://redis:6379/'
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}