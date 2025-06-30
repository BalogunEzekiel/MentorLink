# mentor.py

import streamlit as st
from database import supabase
from datetime import datetime, timedelta
from utils.helpers import format_datetime_safe
from utils.session_creator import create_session_with_meet_and_email
from emailer import send_email


def show():
    st.title("Mentor Dashboard")
    st.info("Manage your sessions, availability, and mentee interactions.")
    mentor_id = st.session_state.user["userid"]

    tabs = st.tabs(["📅 My Sessions", "📌 Add Availability", "✅ Session Feedback"])

    # ---------------------- 📅 My Sessions Tab ----------------------
    with tabs[0]:
        st.subheader("Your Mentorship Sessions")

        sessions = supabase.table("session") \
            .select("*, users!session_menteeid_fkey(email)") \
            .eq("mentorid", mentor_id).execute().data or []

        if sessions:
            for s in sessions:
                mentee_email = s.get("users", {}).get("email", "Unknown")
                session_date = format_datetime_safe(s.get("date"))
                rating = s.get("rating", "Not rated")
                feedback = s.get("feedback", "No feedback")

                st.markdown(f"""
                #### With: {mentee_email}
                - 📅 Date: {session_date}
                - ⭐ Rating: {rating}
                - 💬 Feedback: {feedback}
                """)

                if st.button("📧 Send Reminder", key=f"reminder_{s['sessionid']}"):
                    if send_email(
                        to_email=mentee_email,
                        subject="📅 Mentorship Session Reminder",
                        body=f"This is a reminder for your session scheduled on {session_date}."
                    ):
                        st.success("Reminder email sent!")
                    else:
                        st.error("Failed to send reminder.")
        else:
            st.info("No sessions yet.")

    # ---------------------- 📌 Add Availability Tab ----------------------
    with tabs[1]:
        st.subheader("Add Availability Slot")

        # 👇 Use unique key for the form to prevent duplication error
        with st.form(f"availability_form_{mentor_id}", clear_on_submit=True):
            date = st.date_input("Date", value=datetime.now().date())
            start_time = st.time_input("Start Time", value=(datetime.now() + timedelta(hours=1)).time())
            end_time = st.time_input("End Time", value=(datetime.now() + timedelta(hours=2)).time())

            submitted = st.form_submit_button("➕ Add Slot")

            if submitted:
                start = datetime.combine(date, start_time)
                end = datetime.combine(date, end_time)

                if end <= start:
                    st.warning("End time must be after start time.")
                else:
                    try:
                        supabase.table("availability").insert({
                            "mentorid": mentor_id,
                            "start": start.isoformat(),
                            "end": end.isoformat()
                        }).execute()
                        st.success(f"Availability added: {format_datetime_safe(start)} - {format_datetime_safe(end)}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add availability: {e}")

        # 🗓️ Display existing slots
        st.markdown("### Existing Availability")
        slots = supabase.table("availability").select("*").eq("mentorid", mentor_id).execute().data or []

        if slots:
            for slot in slots:
                start = format_datetime_safe(slot["start"])
                end = format_datetime_safe(slot["end"])
                col1, col2 = st.columns([6, 1])
                col1.markdown(f"- 🕒 {start} ➡ {end}")
                if col2.button("❌", key=f"delete_slot_{slot['availabilityid']}"):
                    try:
                        supabase.table("availability").delete().eq("availabilityid", slot["availabilityid"]).execute()
                        st.success("Availability removed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to remove slot: {e}")
        else:
            st.info("No availability slots added yet.")

    # ---------------------- ✅ Session Feedback Tab ----------------------
    with tabs[2]:
        st.subheader("Rate Mentees & Provide Feedback")

        sessions = supabase.table("session") \
            .select("sessionid, users!session_menteeid_fkey(email), date, rating, feedback") \
            .eq("mentorid", mentor_id).execute().data or []

        for session in sessions:
            if session.get("rating") and session.get("feedback"):
                continue  # Skip already rated sessions

            mentee_email = session.get("users", {}).get("email", "Unknown")
            date_str = format_datetime_safe(session.get("date"))

            with st.expander(f"Session with {mentee_email} on {date_str}"):
                rating = st.selectbox("Rating", [1, 2, 3, 4, 5], key=f"rating_{session['sessionid']}")
                feedback = st.text_area("Feedback", key=f"feedback_{session['sessionid']}")

                if st.button("Submit Feedback", key=f"submit_feedback_{session['sessionid']}"):
                    try:
                        supabase.table("session").update({
                            "rating": rating,
                            "feedback": feedback
                        }).eq("sessionid", session["sessionid"]).execute()
                        st.success("Feedback submitted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error submitting feedback: {e}")
