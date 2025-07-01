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
        # Removed conferenceData to prevent "Invalid conference type value" error
    }

    if attendee:
        event.setdefault('attendees', []).append({'email': attendee})

    try:
        created_event = service.events().insert(
            calendarId='ezekielo.balogun@gmail.com',  # Calendar must be shared with service account
            body=event
        ).execute()

        return None, created_event.get('htmlLink')  # No Meet link, only calendar link

    except HttpError as error:
        st.error("Google Calendar API error occurred:")
        try:
            st.code(error.content.decode("utf-8"), language="json")
        except Exception:
            st.exception(error)
        return None, None
