import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone

SCOPES = ['https://www.googleapis.com/auth/calendar']
USER_EMAIL = 'ezekielo.balogun@gmail.com'  # The Gmail account the calendar is shared with

def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["google_service_account"], scopes=SCOPES
    )
    delegated_credentials = credentials.with_subject(USER_EMAIL)
    return build('calendar', 'v3', credentials=delegated_credentials)

def create_meet_event(start: datetime, end: datetime, summary: str, attendee: str = None):
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {'dateTime': start.astimezone(timezone.utc).isoformat()},
        'end': {'dateTime': end.astimezone(timezone.utc).isoformat()},
        'conferenceData': {
            'createRequest': {
                'requestId': f"meet-{int(start.timestamp())}",
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
