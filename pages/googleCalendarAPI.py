from this import s
from decouple import config
from google.oauth2 import service_account
import googleapiclient.discovery
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
from copy import deepcopy
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

CAL_ID = config('CAL_ID')
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = './google-credentials.json'

def test_calendar():
    #print("RUNNING TEST_CALENDAR()")
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
    return get_events_from_service(service)

def get_token_refresh(refresh_token):
    #print(refresh_token)
    credentials = Credentials(
        token = None,
        client_id = config('CLIENT_ID'), # Please set the client ID.
        client_secret = config('CLIENT_SECRET'), # Please set client secret.
        refresh_token = refresh_token, # Please set refresh token.
        token_uri = config('TOKEN_URI') # Please set token URI.
    )
    credentials.refresh(Request())
    access_token = credentials.token
    #print(access_token)
    return credentials

def get_events_from_service(service):
    today = datetime.today() 
    first_day = today.replace(day=1)
    last_day = first_day + relativedelta(months=1) - relativedelta(days=1)
    #print(today,first_day,last_day )
    tmax = last_day.isoformat('T') + "Z"
    tmin = first_day.isoformat('T') + "Z"
    events_results = service.events().list(calendarId='primary',
        timeMin=tmin,
        timeMax=tmax,
        maxResults=2500, 
        singleEvents=True,
        orderBy='startTime',
    ).execute() 
    events = events_results.get('items', [])
    return events

def round_dt(dt, dir, amount):
    new_minute = (dt.minute // amount + dir) * amount 
    return dt + timedelta(minutes = new_minute - dt.minute)
    
# This is the most important function in my project it has to chunk events in the month into 30 min intervals.  
def get_events(refresh_token,is_book_appointment=False):
    credentials = get_token_refresh(refresh_token)
    service = build('calendar', 'v3', credentials=credentials)
    events = get_events_from_service(service)
    start_dates = [x for x in events if ('date' in x['start'])] 
    #print(start_dates)
    events = [x for x in events if ('date' not in x['start'])]      
    #print(events)
    tz = 'America/Vancouver'
    time_zone = pytz.timezone(tz)

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
        # Make multiple hour datetimes into 30 min chunks and convert timezone if it's book appointment
    if is_book_appointment:
        res=[]
        for e in events:
            # What if you get some start dates in 23 mins, 7 mins? (Todo)
            new_start_time = datetime.strptime(e['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
            new_end_time = datetime.strptime(e['end']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
            converted_start_time = round_dt(new_start_time,0,30)
            converted_end_time = round_dt(new_end_time,1,30)
            time_dif = converted_end_time-converted_start_time
            print(converted_start_time,converted_end_time,time_dif)
            minute_dif = int(round(time_dif.total_seconds()/60, 0))
            half_hours = (minute_dif//30)
            print(minute_dif,half_hours)
            #print("minute dif",minute_dif,"times:",half_hours)
            
            for delta in range(0,30 * half_hours,30):
                #print("delta",delta)
                time_slots = dict(deepcopy(e))
                start = converted_start_time + timedelta(minutes=delta)
                end = converted_start_time + timedelta(minutes=(delta+30))
                time_slots['start']['dateTime'] = start.strftime('%Y-%m-%dT%H:%M:%S%z')
                time_slots['end']['dateTime'] = end.strftime('%Y-%m-%dT%H:%M:%S%z')
                res.append(time_slots)
                #time_slots['start']['timeZone'] = tz
                #time_slots['end']['timeZone'] = tz
                #print(time_slots)
                res.append(time_slots)
        for r in res:
            events.append(r)
	
    #print(events)
    events = sorted(events, key = lambda x:datetime.strptime(x['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z'))
    #print(events)
    """ 
    for e in events:
        print(e) 
    """
    return events

# Make a check to see if time slot is not booked.
def add_appointment(user,doctor,start_time):
    credentials = get_token_refresh(doctor.refresh_token)
    #print(start_time)
    event = {
        'summary': 'Appointment',
        'location': 'Online',
        'description': 'Online appointment',
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Vancouver',
        },
        'end': {
            'dateTime': (datetime.strptime(start_time,'%Y-%m-%dT%H:%M:%S%z')+timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S%z'),
            'timeZone': 'America/Vancouver',
        },
        'attendees': [
            {'email': user.email},
            {'email': doctor.email},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    service = build('calendar', 'v3', credentials=credentials)
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    #print('Event created: %s' % (created_event.get('htmlLink')))

    # Accepts for the users so it's automatically going to update so multiple users don't book the same time slot
    for attendee in event['attendees']:
        attendee['responseStatus'] = 'accepted'
        
    service.events().patch(
        calendarId='primary',
        eventId=created_event['id'],
        body=event
    )