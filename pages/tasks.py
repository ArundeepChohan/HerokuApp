from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime
from .models import Medications, Messages, Profile
from django.db.models.query_utils import Q
import pytz

@shared_task(name = "pages.print_time")
def print_time():
    tz = pytz.timezone('America/Vancouver')
    today = datetime.now(tz)
    current_time = today.strftime("%Y-%m-%dT%H:%M:%S%z")
    print(f"Current Time is {current_time}")
    # Add below line after testing (Todo)
    # &Q(is_staff=False)&Q(is_doctor=False)
    profiles = Profile.objects.filter()
    print(profiles)
    # So for every user that is > 30 and not a doctor set all messages to blocks, 
    # remove google oauth from django, remove media files, 
    for profile in profiles:
        print(profile.date_created)
        dif = today - tz.localize(profile.date_created)
        print(dif.days)
        if dif.days>=30:
            print('Remove this user and set messages to be blocked')
            meds_to_be_deleted = Medications.objects.filter(user=profile.user)
            print(meds_to_be_deleted)

