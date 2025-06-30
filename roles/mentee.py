import streamlit as st
from database import supabase
from utils.helpers import format_datetime
from emailer import send_email
from mentee_requests import show as show_booking  # Handles booking logic UI

def show():
    # Show success message for mentorship request once
    if "mentor_request_success_message" in st.session_state:
        st.success(st.session_state["mentor_request_success_message"])
        del st.session_state["mentor_request_success_message"]

    st.title("Mentee Dashboard")
    st.info("Browse mentors, request sessions, and track bookings.")
    
    if "user" not in st.session_state:
        st.error("Please log in first.")
        return

    user_id = st.session_state.user["userid"]

    tabs = st.tabs(["🧑‍🏫 Browse Mentors", "📄 My Requests", "📌 Book Session", "📆 My Sessions"])

    # ---------------------- 🧑‍🏫 Browse Mentors ----------------------
    with tabs[0]:
        st.subheader("Browse Available Mentors")

        try:
            mentors = supabase.table("users") \
                .select("*, profile(name, bio, skills, goals, profile_image_url)") \
                .eq("role", "Mentor") \
                .neq("status", "Delete") \
                .execute().data
        except Exception as e:
            st.error(f"❌ Failed to load mentors: {e}")
            mentors = []

        if not mentors:
            st.info("No mentors found.")
        else:
            cols = st.columns(2)
            for i, mentor in enumerate(mentors):
                col = cols[i % 2]
                with col:
                    profile = mentor.get("profile", {})
                    name = profile.get("name", "Unnamed Mentor")
                    bio = profile.get("bio", "No bio provided.")
                    skills = profile.get("skills", "Not specified")
                    goals = profile.get("goals", "No goals set")
                    image_url = profile.get("profile_image_url")

                    avatar_url = image_url or f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&size=128&background=ddd&color=555"

                    st.image(avatar_url, width=120, caption=name)
                    st.markdown(f"**Bio:** {bio}")
                    st.markdown(f"**Skills:** {skills}")
                    st.markdown(f"**Goals:** {goals}")

                    try:
                        availability = supabase.table("availability") \
                            .select("availabilityid") \
                            .eq("mentorid", mentor["userid"]) \
                            .execute().data
                    except Exception as e:
                        st.error(f"❌ Could not check availability: {e}")
                        availability = []

                    if availability:
                        if st.button("Request Mentorship", key=f"req_{mentor['userid']}"):
                            try:
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
                                    st.session_state["mentor_request_success_message"] = \
                                        f"✅ Mentorship request sent to {mentor['email']}!"
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to send request: {e}")
                    else:
                        st.warning("This mentor has no availability yet. Please check back later.")

    # ---------------------- 📄 My Requests ----------------------
    with tabs[1]:
        st.subheader("Your Mentorship Requests")
        try:
            requests_result = supabase.table("mentorshiprequest") \
                .select("*, users!mentorshiprequest_mentorid_fkey(email)") \
                .eq("menteeid", user_id).execute()
            requests = requests_result.data
        except Exception as e:
            st.error(f"❌ Failed to fetch mentorship requests: {e}")
            requests = []

        if requests:
            for req in requests:
                mentor_email = req.get("users", {}).get("email", "Unknown")
                status = req.get("status", "Unknown")
                st.markdown(f"- 🧑 Mentor: **{mentor_email}**\n- Status: **{status}**")
        else:
            st.info("You have not made any mentorship requests yet.")

    # ---------------------- 📌 Book Session ----------------------
    with tabs[2]:
        show_booking()

    # ---------------------- 📆 My Sessions ----------------------
    with tabs[3]:
        st.subheader("Your Mentorship Sessions")

        try:
            sessions = supabase.table("session") \
                .select("*, users!session_mentorid_fkey(email)") \
                .eq("menteeid", user_id).execute().data
        except Exception as e:
            st.error(f"❌ Failed to fetch your sessions: {e}")
            sessions = []

        if sessions:
            for s in sessions:
                mentor_email = s.get("users", {}).get("email", "Unknown")
                session_date = format_datetime(s.get("date"))
                rating = s.get("rating", "Pending")
                feedback = s.get("feedback", "Not submitted")

                st.markdown(f"""
                #### With: {mentor_email}
                - 🗓 Date: {session_date}
                - ⭐ Rating: {rating}
                - 💬 Feedback: {feedback}
                """)

                if st.button("Send Reminder Email", key=f"reminder_{s['sessionid']}"):
                    email_sent = send_email(
                        to_email=mentor_email,
                        subject="Session Reminder",
                        body=f"This is a reminder for your mentorship session on {session_date}."
                    )
                    if email_sent:
                        st.success("📧 Email sent successfully!")
                    else:
                        st.error("❌ Failed to send email.")
        else:
            st.info("You don’t have any sessions yet.")
