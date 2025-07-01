import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timezone

# Define the scope and calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    # Authenticate with service account credentials stored in Streamlit secrets
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=credentials)

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

    try:
        created_event = service.events().insert(
            calendarId='ezekielo.balogun@gmail.com',  # The calendar shared with the service account
            body=event,
            conferenceDataVersion=1
        ).execute()

        return created_event.get('hangoutLink'), created_event.get('htmlLink')

    except HttpError as error:
        st.error("Google Calendar API error occurred:")
        try:
            st.code(error.content.decode("utf-8"), language="json")  # Show the detailed JSON error
        except Exception:
            st.exception(error)  # Fallback if decoding fails
        return None, None
