from utils.google_calendar import create_meet_event  # or create_zoom_event
from emailer import send_email
from datetime import datetime
from postgrest.exceptions import APIError

def create_session_with_meet_and_email(supabase, mentor_id, mentee_id, start, end):
    """
    Creates a mentorship session with a Google Meet link and sends email notifications.
    """

    # ✅ 1. Conflict Check (mentor already booked during this slot)
    conflict = supabase.table("session") \
        .select("sessionid") \
        .eq("mentorid", mentor_id) \
        .lte("date", end.isoformat()) \
        .gte("date", start.isoformat()) \
        .execute().data

    if conflict:
        return False, "⚠️ This time slot is already booked for the mentor."

    # ✅ 2. Create Meet Event
    meet_link, cal_link = create_meet_event(start, end, "Mentorship Session")

    if not cal_link:
        return False, "❌ Failed to create calendar event."

    # ✅ 3. Session Record
    session_data = {
        "mentorid": mentor_id,
        "menteeid": mentee_id,
        "date": start.replace(tzinfo=None).isoformat(),  # remove timezone for consistency
        "meet_link": meet_link
    }

    try:
        supabase.table("session").insert(session_data).execute()
    except APIError as e:
        print("❌ Supabase insert failed")
        print("Message:", e.message)
        print("Details:", e.details)
        print("Hint:", e.hint)
        return False, "❌ Failed to save session to database."

    # ✅ 4. Get User Emails
    try:
        mentor = supabase.table("users").select("email").eq("userid", mentor_id).execute().data[0]
        mentee = supabase.table("users").select("email").eq("userid", mentee_id).execute().data[0]
    except Exception as e:
        print("❌ Error fetching user emails:", e)
        return False, "❌ Failed to fetch mentor/mentee emails."

    # ✅ 5. Send Email Notifications
    subject = "📅 Mentorship Session Booked"
    body = f"""
Hi,

Your mentorship session has been scheduled.

🕒 Time: {start.strftime('%A, %d %B %Y at %I:%M %p')} to {end.strftime('%I:%M %p')}
🔗 Join Meeting: {meet_link}
📅 View in Calendar: {cal_link}

Thank you,
MentorLink Team
    """.strip()

    for email in [mentor["email"], mentee["email"]]:
        send_email(email, subject, body)

    return True, f"✅ Session created! [Join Meeting]({meet_link}) | [View Calendar]({cal_link})"

# ✅ Alias for backward compatibility
create_session_if_available = create_session_with_meet_and_email
