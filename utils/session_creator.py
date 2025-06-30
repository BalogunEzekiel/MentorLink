from utils.google_calendar import create_meet_event
from emailer import send_email
from datetime import datetime, timedelta

def create_session_if_available(supabase, mentorid, menteeid, start, end):
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


def create_session_with_meet_and_email(supabase, mentor_id, mentee_id, request_id):
    now = datetime.utcnow()
    end = now + timedelta(hours=1)

    meet_link, cal_link = create_meet_event(now, end, "Mentorship Session", attendee=None)

    # Insert session into Supabase
    supabase.table("session").insert({
        "mentorid": mentor_id,
        "menteeid": mentee_id,
        "date": now.isoformat(),
        "meet_link": meet_link,
        "mentorshiprequestid": request_id
    }).execute()

    # Fetch user emails
    mentor = supabase.table("users").select("email").eq("userid", mentor_id).execute().data[0]
    mentee = supabase.table("users").select("email").eq("userid", mentee_id).execute().data[0]

    # Notify both
    for email in [mentor["email"], mentee["email"]]:
        send_email(email, "Mentorship Session Scheduled",
                   f"Your session has been scheduled.\n📅 Time: {now}\n🔗 Meet link: {meet_link}")

    return True, "✅ Session created and emails sent."
