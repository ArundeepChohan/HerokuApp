from decouple import config
from google.oauth2 import service_account
import googleapiclient.discovery
from datetime import datetime
from dateutil.relativedelta import relativedelta

from portfolio import settings

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
"""     
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
def set_tokens():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('./credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json()) 
 """

def get_access_token(request): 
    social = request.user.social_auth.get(provider='google-oauth2') 
    return social.extra_data['access_token']
