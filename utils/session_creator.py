from utils.google_calendar import create_meet_event  # or create_zoom_event
from emailer import send_email
from datetime import datetime
from postgrest.exceptions import APIError

def create_session_with_meet_and_email(supabase, mentor_id, mentee_id, start, end):
    # ✅ Check if session already exists for the same mentor during the time slot
    conflict = supabase.table("session") \
        .select("sessionid") \
        .eq("mentorid", mentor_id) \
        .lte("date", end.isoformat()) \
        .gte("date", start.isoformat()) \
        .execute().data

    if conflict:
        return False, "⚠️ This time slot is already booked for the mentor."

    # ✅ Create Google Meet or Zoom meeting link
    meet_link, cal_link = create_meet_event(start, end, "Mentorship Session")

    # ✅ Prepare session data
    session_data = {
        "mentorid": mentor_id,
        "menteeid": mentee_id,
        "date": start.replace(tzinfo=None).isoformat(),  # removes timezone info
        "meet_link": meet_link
    }

    # ✅ Save session to Supabase
    try:
        supabase.table("session").insert(session_data).execute()
    except APIError as e:
        print("❌ Supabase insert failed")
        print("Message:", e.message)
        print("Details:", e.details)
        print("Hint:", e.hint)
        return False, "❌ Failed to save session to database."

    # ✅ Fetch participant emails
    try:
        mentor = supabase.table("users").select("email").eq("userid", mentor_id).execute().data[0]
        mentee = supabase.table("users").select("email").eq("userid", mentee_id).execute().data[0]
    except Exception:
        return False, "❌ Failed to fetch mentor/mentee emails."

    # ✅ Send email notifications
    for email in [mentor["email"], mentee["email"]]:
        send_email(
            email,
            "📅 Mentorship Session Booked",
            f"Hi,\n\nYour session is scheduled from {start} to {end}.\nJoin using: {meet_link}"
        )

    return True, f"✅ Session created! [Join Meeting]({meet_link}) | [View in Calendar]({cal_link})"

# Make alias
create_session_if_available = create_session_with_meet_and_email
