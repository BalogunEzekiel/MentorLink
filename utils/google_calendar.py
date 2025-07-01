import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone

# Define the scope and calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    # Authenticate with service account credentials stored in Streamlit secrets
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=SCOPES
    )
    
    # DO NOT use with_subject() for personal Gmail — it will cause a RefreshError
    return build('calendar', 'v3', credentials=credentials)

def create_meet_event(start: datetime, end: datetime, summary: str, attendee: str = None):
    service = get_calendar_service()
    
    # Define event with Meet link creation
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

    # Insert the event into the shared calendar
    created_event = service.events().insert(
        calendarId='primary',  # This works if the calendar is owned by the service account or shared with it
        body=event,
        conferenceDataVersion=1
    ).execute()

    return created_event.get('hangoutLink'), created_event.get('htmlLink')
