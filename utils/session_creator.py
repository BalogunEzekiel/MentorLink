# utils/session_creator.py

from .google_calendar import create_meet_event
from emailer import send_email

def create_session_with_meet_and_email(supabase, mentorid, menteeid, start, end):
    # conflict checks omitted for brevity

    meet_link, cal_link = create_meet_event(start, end, "Mentorship Session", attendee=None)
    res = supabase.table("session").insert({
        "mentorid": mentorid,
        "menteeid": menteeid,
        "date": start.isoformat(),
        "meet_link": meet_link
    }).execute()

    # Auto-email both participants
    mentor = supabase.table("users").select("email").eq("userid", mentorid).execute().data[0]
    mentee = supabase.table("users").select("email").eq("userid", menteeid).execute().data[0]
    for user in [mentor["email"], mentee["email"]]:
        send_email(user, "Mentorship Session Scheduled",
                   f"Your session is scheduled at {start}.\nJoin via Meet: {meet_link}")
    return True, "Session created with Meet link and reminder emails"
