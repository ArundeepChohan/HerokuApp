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
    
from google.oauth2.credentials import Credentials
def get_user_events(request):
    credentials = Credentials(get_access_token(request), 'USER_AGENT')
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
    google_calendar_events = service.events().list(calendarId='primary', singleEvents=True,
                                          orderBy='startTime').execute()
    google_calendar_events = google_calendar_events.get('items', [])
    return google_calendar_events

def get_access_token(request): 
    social = request.user.social_auth.get(provider='google-oauth2') 
    return social.extra_data['access_token']