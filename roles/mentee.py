import streamlit as st
from database import supabase
from utils.helpers import format_datetime, format_datetime_safe
from utils.session_creator import create_session_with_meet_and_email
from emailer import send_email
from datetime import datetime, timedelta

def show():
    if "mentor_request_success_message" in st.session_state:
        st.success(st.session_state.pop("mentor_request_success_message"))

    st.title("Mentee Dashboard")
    st.info("Browse mentors, request sessions, and track bookings.")
    user_id = st.session_state.user["userid"]

    tabs = st.tabs(["🧑‍🏫 Browse Mentors", "📄 My Requests", "📌 Book Session", "📆 My Sessions"])

    # ---------------------- 🧑‍🏫 Browse Mentors Tab ----------------------
    with tabs[0]:
        st.subheader("Browse Available Mentors")
        mentors = supabase.table("users").select("*, profile(name, bio, skills, goals, profile_image_url)") \
            .eq("role", "Mentor").execute().data or []

        if not mentors:
            st.info("No mentors available.")
        else:
            cols = st.columns(2)
            for i, mentor in enumerate(mentors):
                col = cols[i % 2]
                with col:
                    profile = mentor.get("profile") or {}
                    if not isinstance(profile, dict):
                        profile = {}

                    name = profile.get("name", "Unnamed Mentor")
                    avatar_url = profile.get("profile_image_url") or f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&size=128"
                    bio = profile.get("bio", "No bio")
                    skills = profile.get("skills", "Not listed")
                    goals = profile.get("goals", "Not set")

                    st.image(avatar_url, width=120, caption=name)
                    st.markdown(f"**Bio:** {bio}  \n**Skills:** {skills}  \n**Goals:** {goals}")

                    availability = supabase.table("availability") \
                        .select("availabilityid") \
                        .eq("mentorid", mentor["userid"]) \
                        .execute().data or []

                    if availability:
                        if st.button("Request Mentorship", key=f"req_{mentor['userid']}"):
                            existing = supabase.table("mentorshiprequest") \
                                .select("mentorshiprequestid", "status") \
                                .eq("menteeid", user_id) \
                                .eq("mentorid", mentor["userid"]) \
                                .in_("status", ["PENDING", "ACCEPTED"]) \
                                .execute().data

                            if existing:
                                st.warning("❗ You already have a pending or accepted request with this mentor.")
                            else:
                                supabase.table("mentorshiprequest").insert({
                                    "mentorid": mentor["userid"],
                                    "menteeid": user_id,
                                    "status": "PENDING"
                                }).execute()
                                st.session_state["mentor_request_success_message"] = f"✅ Request sent to {mentor['email']}!"
                                st.rerun()
                    else:
                        st.warning("This mentor has no availability yet.")

    # ---------------------- 📄 My Requests Tab ----------------------
    with tabs[1]:
        st.subheader("Your Mentorship Requests")
        requests = supabase.table("mentorshiprequest") \
            .select("*, users!mentorshiprequest_mentorid_fkey(email)") \
            .eq("menteeid", user_id).execute().data or []

        if requests:
            for req in requests:
                mentor_email = req.get("users", {}).get("email", "Unknown")
                st.markdown(f"- 🧑 Mentor: **{mentor_email}**\n- Status: **{req.get('status', 'Unknown')}**")
        else:
            st.info("You have not made any mentorship requests yet.")

    # ---------------------- 📌 Book Session Tab ----------------------
    with tabs[2]:
        st.subheader("Book a Session")
        mentors = supabase.table("users").select("userid, email").eq("role", "Mentor").execute().data or []
        mentor_email_list = [m["email"] for m in mentors]

        mentor_email = st.selectbox("Select a Mentor", mentor_email_list)
        selected_date = st.date_input("Select Date", value=datetime.now().date())
        selected_time = st.time_input("Select Start Time", value=(datetime.now() + timedelta(hours=1)).time())
        start = datetime.combine(selected_date, selected_time)

        end_time = st.time_input("Select End Time", value=(start + timedelta(hours=1)).time())
        end = datetime.combine(selected_date, end_time)

        if st.button("📌 Book Session"):
            if end <= start:
                st.warning("End time must be after start time.")
            else:
                mentor_id = next((m["userid"] for m in mentors if m["email"] == mentor_email), None)
                success, message = create_session_if_available(supabase, mentor_id, user_id, start, end)
                st.success(message) if success else st.error(message)

    # ---------------------- 📆 My Sessions Tab ----------------------
    with tabs[3]:
        st.subheader("Your Mentorship Sessions")
        sessions = supabase.table("session") \
            .select("*, users!session_mentorid_fkey(email)") \
            .eq("menteeid", user_id).execute().data or []

        if sessions:
            for s in sessions:
                mentor_email = s.get("users", {}).get("email", "Unknown")
                session_date = format_datetime_safe(s.get("date"))
                rating = s.get("rating", "Pending")
                feedback = s.get("feedback", "Not submitted")

                st.markdown(f"""
                #### With: {mentor_email}
                - 📅 Date: {session_date}
                - ⭐ Rating: {rating}
                - 💬 Feedback: {feedback}
                """)

                if st.button("📧 Send Reminder", key=f"reminder_{s['sessionid']}"):
                    if send_email(
                        to_email=mentor_email,
                        subject="📅 Session Reminder",
                        body=f"Reminder for your session on {session_date}."
                    ):
                        st.success("Reminder email sent!")
                    else:
                        st.error("Failed to send email.")
        else:
            st.info("You don’t have any sessions yet.")
