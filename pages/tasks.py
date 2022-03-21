from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime

@shared_task(name = "pages.print_time")
def print_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time is ")

