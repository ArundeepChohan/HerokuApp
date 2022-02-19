
from decouple import config
from google.oauth2 import service_account

import googleapiclient.discovery
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
    last_day = first_day + relativedelta(months=1)- relativedelta(days=1)
    print(today,first_day,last_day )
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
    for e in events:
        print(e)
    #uncomment the following lines to delete each existing item in the calendar
    #event_id = e['id']
        # service.events().delete(calendarId=CAL_ID, eventId=event_id).execute() 
    return events 

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
def get_events(refresh_token):
    print(refresh_token)
    credentials = Credentials(
        token=None,
        client_id = config('CLIENT_ID'), # Please set the cliend ID.
        client_secret = config('CLIENT_SECRET'), # Please set client secret.
        refresh_token = refresh_token, # Please set refresh token.
        token_uri = config('TOKEN_URI') # Please set token URI.
    )
    credentials.refresh(Request())
    access_token = credentials.token
    print(access_token)

    service = build('calendar', 'v3', credentials=credentials)
    today = datetime.today() 
    first_day = today.replace(day=1)
    last_day = first_day + relativedelta(months=1)- relativedelta(days=1)
    print(today,first_day,last_day )
    tmax = last_day.isoformat('T') + "Z"
    tmin = first_day.isoformat('T') + "Z"
    personal_events = service.events().list(calendarId='primary',
        timeMin=tmin,
        timeMax=tmax,
        maxResults=2500, 
        singleEvents=True,
        orderBy='startTime',
    ).execute() 
    personal_events = personal_events.get('items', [])
    for e in personal_events:
        print(e)
    return personal_events