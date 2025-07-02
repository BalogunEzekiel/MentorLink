# utils/google_meet.py
from google_auth import get_calendar_service
from datetime import datetime
import pytz


def create_meet_link(summary, description, start_time, end_time, attendees):
    service = get_calendar_service()

    timezone = "Africa/Lagos"
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
        "attendees": [{"email": email} for email in attendees],
        "conferenceData": {
            "createRequest": {
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
                "requestId": f"meet-{int(datetime.now().timestamp())}"
            }
        }
    }

    try:
        event = service.events().insert(
            calendarId='primary',  # or replace with custom calendar ID
            body=event,
            conferenceDataVersion=1
        ).execute()

        return event.get("hangoutLink")
    except Exception as e:
        print(f"Error creating Meet link: {e}")
        return None
