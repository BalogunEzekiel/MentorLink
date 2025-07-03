# utils/google_meet.py
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone
import pytz

# Required Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Authenticates and returns a Google Calendar API service object using
    a service account key stored in Streamlit secrets.
    """
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=credentials)
    return service

def create_meet_link(summary, description, start_time, end_time, attendees):
    """
    Creates a Google Calendar event with a Google Meet link.

    Args:
        summary (str): Event title.
        description (str): Event description.
        start_time (datetime): Start time (timezone-aware).
        end_time (datetime): End time (timezone-aware).
        attendees (list of str): List of attendee emails.

    Returns:
        str or None: The Google Meet join URL if successful, else None.
    """
    service = get_calendar_service()

    # Lagos timezone string
    timezone_str = "Africa/Lagos"

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": timezone_str,
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": timezone_str,
        },
        "attendees": [{"email": email} for email in attendees] if attendees else [],
        "conferenceData": {
            "createRequest": {
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
                "requestId": f"meet-{int(datetime.now(timezone.utc).timestamp())}"
            }
        },
        "reminders": {
            "useDefault": True
        }
    }

    try:
        created_event = service.events().insert(
            calendarId='primary',  # Replace if you want to use a specific calendar ID shared with your service account
            body=event,
            conferenceDataVersion=1
        ).execute()

        # Extract the Google Meet link from the conferenceData entry points
        meet_link = None
        conference_data = created_event.get("conferenceData", {})
        entry_points = conference_data.get("entryPoints", [])
        for entry in entry_points:
            if entry.get("entryPointType") == "video":
                meet_link = entry.get("uri")
                break

        return meet_link

    except Exception as e:
        print(f"Error creating Meet link: {e}")
        return None
