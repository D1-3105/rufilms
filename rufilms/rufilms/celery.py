import os
from celery import Celery
from . import celeryconf

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rufilms.settings')

app = Celery('rufilms')

app.config_from_object(celeryconf, namespace='CELERY')

app.conf.timezone='UTC'

app.autodiscover_tasks()
print('HERE')
CELERYBEAT_SCHEDULE = {

}