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
                "requestId": f"meet-{datetime.now().timestamp()}"
            }
        }
    }

    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    return event.get("hangoutLink")

# google_auth.py
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle, os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)

# integration into session creation
# session_creator.py
from utils.google_meet import create_meet_link


def create_session_if_available(supabase, mentor_id, mentee_id, start, end, mentor_email, mentee_email):
    # Check for overlapping sessions
    overlapping = supabase.table("session").select("*") \
        .eq("mentorid", mentor_id) \
        .lt("end_time", end.isoformat()) \
        .gt("date", start.isoformat()).execute().data

    if overlapping:
        return False, "⚠️ This time slot overlaps with another session."

    try:
        meet_link = create_meet_link(
            summary="Mentorship Session",
            description="1:1 mentorship session",
            start_time=start,
            end_time=end,
            attendees=[mentor_email, mentee_email]
        )

        supabase.table("session").insert({
            "mentorid": mentor_id,
            "menteeid": mentee_id,
            "date": start.isoformat(),
            "end_time": end.isoformat(),
            "status": "Scheduled",
            "meet_link": meet_link
        }).execute()

        return True, "✅ Session booked with Meet link created."
    except Exception as e:
        return False, f"❌ Failed to create Meet link: {e}"
