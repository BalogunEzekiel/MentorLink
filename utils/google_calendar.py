import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timezone

# Define the required scope for calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    # Authenticate with service account credentials from Streamlit secrets
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=credentials)

def create_meet_event(start: datetime, end: datetime, summary: str, attendee: str = None):
    """
    Create a Google Calendar event with Google Meet link.

    Args:
        start (datetime): Start datetime (timezone-aware)
        end (datetime): End datetime (timezone-aware)
        summary (str): Event title/summary
        attendee (str, optional): Email address to invite

    Returns:
        Tuple[None or str, str or None]: (error message or None, calendar event link or None)
    """
    try:
        service = get_calendar_service()

        event = {
            'summary': summary,
            'start': {
                'dateTime': start.astimezone(timezone.utc).isoformat(),
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': end.astimezone(timezone.utc).isoformat(),
                'timeZone': 'UTC'
            },
            # Optional Google Meet conference data
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{start.timestamp()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            },
            'reminders': {
                'useDefault': True
            }
        }

        if attendee:
            event['attendees'] = [{'email': attendee}]

        created_event = service.events().insert(
            calendarId='ezekielo.balogun@gmail.com',  # Make sure your service account has access!
            body=event,
            conferenceDataVersion=1
        ).execute()

        calendar_link = created_event.get('htmlLink')
        return None, calendar_link

    except HttpError as error:
        st.error("🚫 Google Calendar API error occurred:")
        try:
            st.code(error.content.decode("utf-8"), language="json")
        except Exception:
            st.exception(error)
        return "Google Calendar API error", None
    except Exception as general_error:
        st.error("❌ Unexpected error while creating event:")
        st.exception(general_error)
        return "Unexpected error", None
