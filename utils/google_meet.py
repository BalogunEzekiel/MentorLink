# utils/google_meet.py
from google_auth import get_calendar_service
from datetime import datetime
import pytz

def create_meet_link(summary, description, start_time, end_time, attendees):
    """
    Creates a Google Meet event on the calendar with given details.

    Args:
        summary (str): Event title.
        description (str): Event description.
        start_time (datetime): Start time (should be timezone-aware).
        end_time (datetime): End time (should be timezone-aware).
        attendees (list of str): List of attendee emails.

    Returns:
        str or None: The Google Meet join URL if successful, else None.
    """
    service = get_calendar_service()

    timezone = "Africa/Lagos"  # Use Lagos timezone

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": timezone,
        },
        "attendees": [{"email": email} for email in attendees] if attendees else [],
        "conferenceData": {
            "createRequest": {
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
                "requestId": f"meet-{int(datetime.now().timestamp())}"
            }
        }
    }

    try:
        created_event = service.events().insert(
            calendarId='primary',  # or your custom calendar ID
            body=event,
            conferenceDataVersion=1
        ).execute()

        meet_link = created_event.get("hangoutLink")
        return meet_link
    except Exception as e:
        print(f"Error creating Meet link: {e}")
        return None
