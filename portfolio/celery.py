from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from decouple import config
from celery.schedules import crontab
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
app = Celery('portfolio')
app.conf.update(BROKER_URL=config('REDIS_URL'),
                CELERY_RESULT_BACKEND=config('REDIS_URL'))
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
#lambda: settings.INSTALLED_APPS
app.autodiscover_tasks()
#from django.apps import apps
#app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

# There are used for periodic request which use tasks.py
app.conf.beat_schedule = {
    #Scheduler Name
    'print-message-once-and-then-every-minute': {
        # Task Name (Name Specified in Decorator)
        'task': 'pages.print_time',  
        # Schedule      
        'schedule': crontab(minute='*/1')
    },
}