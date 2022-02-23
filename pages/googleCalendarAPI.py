
from decouple import config
from google.oauth2 import service_account

import googleapiclient.discovery
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
from copy import deepcopy

CAL_ID = config('CAL_ID')
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = './google-credentials.json'

def test_calendar():

    print("RUNNING TEST_CALENDAR()")
    
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
    
    # GET ALL EXISTING EVENTS Max 2500 in this month
    today = datetime.today() 
    first_day = today.replace(day=1)
    last_day = first_day + relativedelta(months=1) - relativedelta(days=1)
    #print(today,first_day,last_day )
    tmax = last_day.isoformat('T') + "Z"
    tmin = first_day.isoformat('T') + "Z"
    #camelcase usage due to services check if can switch to lowercase_with_underscores
    events_result = service.events().list(
        calendarId=CAL_ID,
        timeMin=tmin,
        timeMax=tmax,
        maxResults=2500,
        singleEvents=True,
        orderBy='startTime',
    ).execute()
    events = events_result.get('items', [])
    """ 
    for e in events:
        print(e)  
    """
    return events 

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
def get_events(refresh_token,is_book_appointment=False):
    #print(refresh_token)
    credentials = Credentials(
        token=None,
        client_id = config('CLIENT_ID'), # Please set the client ID.
        client_secret = config('CLIENT_SECRET'), # Please set client secret.
        refresh_token = refresh_token, # Please set refresh token.
        token_uri = config('TOKEN_URI') # Please set token URI.
    )
    credentials.refresh(Request())
    access_token = credentials.token
    #print(access_token)

    service = build('calendar', 'v3', credentials=credentials)
    today = datetime.today() 
    first_day = today.replace(day=1)
    last_day = first_day + relativedelta(months=1) - relativedelta(days=1)
    #print(today,first_day,last_day )
    tmax = last_day.isoformat('T') + "Z"
    tmin = first_day.isoformat('T') + "Z"
    events = service.events().list(calendarId='primary',
        timeMin=tmin,
        timeMax=tmax,
        maxResults=2500, 
        singleEvents=True,
        orderBy='startTime',
    ).execute() 
    events = events.get('items', [])
    # This is the most important function in my project it has to chunk events in the month into 30 min intervals.
    start_dates = [x for x in events if ('date' in x['start'])] 
    print(start_dates)
    events = [x for x in events if ('date' not in x['start'])]      
    print(events)
    tz='America/Vancouver'
    time_zone = pytz.timezone(tz)
    # Make multiple hour datetimes into 30 min chunks and convert timezone if it's book appointment
    if is_book_appointment:
        res=[]
        for e in events:
            start_time = datetime.strptime(e['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
            end_time = datetime.strptime(e['end']['dateTime'], '%Y-%m-%dT%H:%M:%S%z') 
            time_dif = end_time - start_time
            minute_dif = int(round(time_dif.total_seconds()/60, 0))
            half_hours=(minute_dif//30)
            print("minute dif",minute_dif,"times:",half_hours)
            
            for delta in range(0,30*half_hours,30):
                print("delta",delta)
                time_slots = dict(deepcopy(e))
                start = start_time + timedelta(minutes=delta)
                end = start_time + timedelta(minutes=(delta+30))
                time_slots['start']['dateTime'] = start.strftime('%Y-%m-%dT%H:%M:%S%z')
                time_slots['end']['dateTime'] = end.strftime('%Y-%m-%dT%H:%M:%S%z')
                #time_slots['start']['timeZone'] = tz
                #time_slots['end']['timeZone'] = tz
                #print(time_slots)
                res.append(time_slots)

            if minute_dif>=30:
                events.remove(e)
        for r in res:
            events.append(r)
    for event in start_dates:
        new_start_time = datetime.strptime(event['start']['date'], '%Y-%m-%d' )
        new_end_time = datetime.strptime(event['end']['date'], '%Y-%m-%d' ) 
        #print(new_start_time,new_end_time)
        del event['start']['date']
        del event['end']['date']
		# Loop through each day
        while new_start_time < new_end_time:
            new = dict(deepcopy(event))
            #print(new_start_time,new_end_time)
            vancouver_time = time_zone.localize(new_start_time)
            #print(vancouver_time)
			# Append to events to create a day long datetime for calendar.html or multiple time slots for bookappointment 				
            if is_book_appointment:
                for delta in range(0, 30 * 48, 30):
                    time_slots = dict(deepcopy(event))
                    start = vancouver_time + timedelta(minutes=delta)
                    end = vancouver_time + timedelta(minutes=delta+30)
                    time_slots['start']['dateTime'] = start.strftime('%Y-%m-%dT%H:%M:%S%z')
                    time_slots['end']['dateTime'] = end.strftime('%Y-%m-%dT%H:%M:%S%z')
                    time_slots['start']['timeZone'] = tz
                    time_slots['end']['timeZone'] = tz
                    #print(time_slots)
                    events.append(time_slots)			
            else: 
			    # The end date is just the current day
                new['start']['dateTime'] = vancouver_time.strftime('%Y-%m-%dT%H:%M:%S%z')
                new['end']['dateTime'] = (vancouver_time+relativedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S%z')
                new['start']['timeZone'] = tz
                new['end']['timeZone'] = tz
                #print(new)
                events.append(new)
            new_start_time = new_start_time+relativedelta(days=1)
	
    for e in events:
        print(e)
    
    return events
