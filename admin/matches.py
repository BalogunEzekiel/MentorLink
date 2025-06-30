import streamlit as st
from datetime import datetime, timedelta
from database import supabase
from utils.session_creator import create_session_if_available
from utils.google_calendar import create_meet_event
from emailer import send_email

def show():
    st.subheader("🔁 Match & Book Sessions")

    try:
        users = supabase.table("users") \
            .select("userid, email, role") \
            .neq("status", "Delete") \
            .execute().data
    except Exception as e:
        st.error(f"Failed to fetch users: {e}")
        return

    mentors = [u for u in users if u["role"] == "Mentor"]
    mentees = [u for u in users if u["role"] == "Mentee"]

    if not mentors or not mentees:
        st.warning("⚠️ No available mentors or mentees.")
        return

    mentee_email = st.selectbox("👤 Select Mentee", [m["email"] for m in mentees])
    mentor_email = st.selectbox("🧑‍🏫 Select Mentor", [m["email"] for m in mentors])

    if st.button("✅ Create Match and Book Session"):
        mentee_id = next(u["userid"] for u in mentees if u["email"] == mentee_email)
        mentor_id = next(u["userid"] for u in mentors if u["email"] == mentor_email)

        try:
            existing = supabase.table("mentorshiprequest") \
                .select("*") \
                .eq("menteeid", mentee_id) \
                .eq("mentorid", mentor_id) \
                .execute().data
        except Exception as e:
            st.error(f"❌ Failed to check existing requests: {e}")
            return

        if existing:
            st.warning("⚠️ A request already exists between these users.")
            return

        # Create mentorship request
        try:
            result = supabase.table("mentorshiprequest").insert({
                "menteeid": mentee_id,
                "mentorid": mentor_id,
                "status": "ACCEPTED"
            }).execute()
            request_id = result.data[0]["mentorshiprequestid"]
        except Exception as e:
            st.error(f"❌ Failed to create mentorship request: {e}")
            return

        # Prepare session details
        start = datetime.utcnow()
        end = start + timedelta(minutes=30)

        # Create Google Meet event
        try:
            meet_link, calendar_link = create_meet_event(
                start, end,
                summary="Mentorship Session",
                attendee=None  # Optional: pass mentee_email
            )
        except Exception as e:
            st.error(f"❌ Failed to generate Google Meet link: {e}")
            return

        # Save session in DB
        try:
            session_result = supabase.table("session").insert({
                "mentorid": mentor_id,
                "menteeid": mentee_id,
                "mentorshiprequestid": request_id,
                "date": start.isoformat(),
                "meet_link": meet_link
            }).execute()
        except Exception as e:
            st.error(f"❌ Failed to save session: {e}")
            return

        # Email notifications
        try:
            subject = "🔔 Mentorship Session Scheduled"
            message = f"""
Hi,

Your mentorship session has been scheduled!

🗓 Date & Time: {start.strftime('%A, %d %B %Y at %I:%M %p')} UTC  
🔗 Google Meet Link: {meet_link}

Best regards,  
MentorLinks Team
            """
            send_email(mentor_email, subject, message)
            send_email(mentee_email, subject, message)
        except Exception as e:
            st.error(f"⚠️ Session created but email failed: {e}")
            return

        st.success("🎉 Session booked and emails sent!")
        st.markdown(f"[Click to Join Meet]({meet_link})")
