# utils/google_calendar.py

import os
import pickle
from datetime import datetime, timezone
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS = 'credentials.json'
TOKEN = 'token.pkl'

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN):
        with open(TOKEN, 'rb') as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN, 'wb') as f:
            pickle.dump(creds, f)
    return build('calendar', 'v3', credentials=creds)

def create_meet_event(start: datetime, end: datetime, summary: str, attendee: str = None):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {'dateTime': start.astimezone(timezone.utc).isoformat()},
        'end': {'dateTime': end.astimezone(timezone.utc).isoformat()},
        'conferenceData': {
            'createRequest': {
                'requestId': f"meet-{start.timestamp()}",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        }
    }
    if attendee:
        event.setdefault('attendees', []).append({'email': attendee})

    created = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()
    return created.get('hangoutLink'), created.get('htmlLink')
