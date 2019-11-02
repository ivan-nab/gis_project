import environ
from gis_project.settings.base import *

env = environ.Env()

DATABASES = {
    'default': env.db()
}
CELERY_BROKER_URL = env('CLOUDAMQP_URL')
CELERY_RESULT_BACKEND = env('REDIS_URL')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
