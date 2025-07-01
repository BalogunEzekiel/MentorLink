from utils.google_calendar import create_meet_event  # or create_zoom_event
from emailer import send_email
from datetime import datetime
from postgrest.exceptions import APIError

def create_session_with_meet_and_email(supabase, mentor_id, mentee_id, start, end):
    # ✅ Check for conflict: any existing session for the mentor in this slot
    conflict = supabase.table("session") \
        .select("sessionid") \
        .eq("mentorid", mentor_id) \
        .lte("date", end.isoformat()) \
        .gte("date", start.isoformat()) \
        .execute().data

    if conflict:
        return False, "⚠️ This time slot is already booked for the mentor."

    # ✅ Create Google Meet link
    meet_link, cal_link = create_meet_event(start, end, "Mentorship Session")

    # ✅ Build session data
    session_data = {
        "mentorid": mentor_id,
        "menteeid": mentee_id,
        "date": start.replace(tzinfo=None).isoformat(),  # strip timezone
        "meet_link": meet_link
    }

    # ✅ Insert into Supabase
    try:
        supabase.table("session").insert(session_data).execute()
    except APIError as e:
        print("❌ Supabase insert failed")
        print("Message:", e.message)
        print("Details:", e.details)
        print("Hint:", e.hint)
        return False, "❌ Failed to save session to database."

    # ✅ Get user emails
    try:
        mentor = supabase.table("users").select("email").eq("userid", mentor_id).execute().data[0]
        mentee = supabase.table("users").select("email").eq("userid", mentee_id).execute().data[0]
    except Exception:
        return False, "❌ Failed to fetch mentor/mentee emails."

    # ✅ Notify both
    for email in [mentor["email"], mentee["email"]]:
        send_email(
            email,
            "📅 Mentorship Session Booked",
            f"Hi,\n\nYour session is scheduled from {start} to {end}.\nJoin here: {meet_link}"
        )

    return True, f"✅ Session created! [Join Meeting]({meet_link}) | [Calendar]({cal_link})"

# ✅ Alias (for admin.py and mentee.py compatibility)
create_session_if_available = create_session_with_meet_and_email
