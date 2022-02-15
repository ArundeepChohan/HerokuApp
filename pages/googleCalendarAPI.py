
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
    # Currently gets 1 - today's date not 1-30(Rework necessary)
    today = datetime.today() 
    monthAgo = today - relativedelta(months=1)
    tmax = today.isoformat('T') + "Z"
    tmin = monthAgo.isoformat('T') + "Z"
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
def get_events(request):
    print(request.user.refresh_token)
    credentials = Credentials(
    token=None,
    client_id="1096935503743-ql3p8h42k41v04b6f1c4l15c2d3vvgnf.apps.googleusercontent.com", # Please set the cliend ID.
    client_secret="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", # Please set client secret.
    refresh_token= request.user.refresh_token, # Please set refresh token.
    token_uri="https://oauth2.googleapis.com/token" # Please set token URI.
)
    #tokenFile = './credentials.json' # Please set the filename with the path.
    #credentials =  Credentials.from_authorized_user_file(tokenFile, scopes=SCOPES)
    credentials.refresh(Request())
    access_token = credentials.token
    print(access_token)

    service = build('calendar', 'v3', credentials=credentials)
    today = datetime.today() 
    monthAgo = today - relativedelta(months=1)
    tmax = today.isoformat('T') + "Z"
    tmin = monthAgo.isoformat('T') + "Z"
    personal_events = service.events().list(calendarId='primary',
        timeMin=tmin,
        timeMax=tmax,
        maxResults=2500, 
        singleEvents=True,
        orderBy='startTime').execute()
    personal_events = personal_events.get('items', [])
    for e in personal_events:
        print(e)
    return personal_events