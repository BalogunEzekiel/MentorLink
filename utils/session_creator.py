from utils.google_calendar import create_meet_event
from emailer import send_email
from datetime import datetime

def create_session_with_meet_and_email(supabase, mentor_id, mentee_id, start, end):
    # ✅ Optional: Check if session already exists for the time slot
    conflict = supabase.table("session") \
        .select("sessionid") \
        .eq("mentorid", mentor_id) \
        .lte("date", end.isoformat()) \
        .gte("date", start.isoformat()) \
        .execute().data

    if conflict:
        return False, "⚠️ This time slot is already booked for the mentor."

    # ✅ Create Google Meet event
    meet_link, cal_link = create_meet_event(start, end, "Mentorship Session")

    # ✅ Save session to database
    supabase.table("session").insert({
        "mentorid": mentor_id,
        "menteeid": mentee_id,
        "date": start.isoformat(),
        "meet_link": meet_link
    }).execute()

    # ✅ Fetch participant emails
    mentor = supabase.table("users").select("email").eq("userid", mentor_id).execute().data[0]
    mentee = supabase.table("users").select("email").eq("userid", mentee_id).execute().data[0]

    # ✅ Notify both via email
    for email in [mentor["email"], mentee["email"]]:
        send_email(email, "📅 Mentorship Session Booked",
                   f"Hi,\n\nYour session is scheduled for {start} - {end}.\nJoin via Google Meet: {meet_link}")

    return True, "✅ Session created with Meet link and notifications sent."
