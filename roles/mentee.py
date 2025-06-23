# Mentee dashboard, find mentor, book sessions
import streamlit as st
from database import supabase
from utils.helpers import format_datetime
from emailer import send_email

def show():
    st.title("Mentee Dashboard")
    st.info("Browse mentors, request sessions, and track bookings.")
    user_id = st.session_state.user["userid"]

    st.header("🧑‍🏫 Browse Mentors")
    mentors = supabase.table("users").select("*").eq("role", "Mentor").execute().data
    for mentor in mentors:
        st.subheader(mentor["email"])
        if st.button("Request Mentorship", key=mentor["userid"]):
            supabase.table("mentorshiprequest").insert({
                "mentorid": mentor["userid"],
                "menteeid": user_id,
                "status": "PENDING"
            }).execute()
            st.success("Mentorship request sent!")

    st.header("📄 My Requests")
    requests = supabase.table("mentorshiprequest") \
        .select("*, users!mentorshiprequest_mentorid_fkey(email)") \
        .eq("menteeid", user_id).execute().data
    for req in requests:
        st.markdown(f"""
        - 🧑 Mentor: **{req['users']['email']}**
        - Status: **{req['status']}**
        """)

    st.header("📆 My Sessions")
    sessions = supabase.table("session") \
        .select("*, users!session_mentorid_fkey(email)") \
        .eq("menteeid", user_id).execute().data

    for s in sessions:
        st.markdown(f"""
        #### With: {s['users']['email']}
        - Date: {format_datetime(s['date'])}
        - Rating: {s.get('rating', 'Pending')}
        - Feedback: {s.get('feedback', 'Not submitted')}
        """)
        if st.button(f"Send Reminder Email", key=s["sessionid"]):
            email_sent = send_email(
                to_email=s["users"]["email"],
                subject="Session Reminder",
                body=f"This is a reminder for your mentorship session on {format_datetime(s['date'])}."
            )
            if email_sent:
                st.success("Email sent successfully!")
            else:
                st.error("Failed to send email.")
