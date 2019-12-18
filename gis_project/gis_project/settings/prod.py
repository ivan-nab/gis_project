import os
from urlparse import urlparse

import environ

from gis_project.settings.base import *

env = environ.Env()

DATABASES = {
    'default': env.db()
}
CELERY_BROKER_URL = env('CLOUDAMQP_URL')
CELERY_RESULT_BACKEND = env('REDIS_URL')
SECRET_KEY = env('SECRET_KEY')
OPENROUTESERVICE_API_KEY = env('OPENROUTESERVICE_API_KEY')
ALLOWED_HOSTS = ['.herokuapp.com']
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

es = urlparse(os.environ.get('SEARCHBOX_URL') or 'http://127.0.0.1:9200/')

port = es.port or 80

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack_elasticsearch.elasticsearch5.Elasticsearch5SearchEngine',
        'URL': es.scheme + '://' + es.hostname + ':' + str(port),
        'INDEX_NAME': 'documents',
    },
}

if es.username:
    HAYSTACK_CONNECTIONS['default']['KWARGS'] = {"http_auth": es.username + ':' + es.password}
