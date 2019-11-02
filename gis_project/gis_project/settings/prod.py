import environ
from gis_project.settings.base import *

env = environ.Env()

DATABASES = {
    'default': env.db()
}
CELERY_BROKER_URL = env('CLOUDAMQP_URL')
CELERY_RESULT_BACKEND = env.cache('REDIS_URL')
CACHES = {'default': env.cache('REDIS_URL')}
