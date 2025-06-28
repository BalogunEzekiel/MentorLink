import streamlit as st
from database import supabase
from utils.helpers import format_datetime
from emailer import send_email
from mentee_requests import show as show_booking
import time

def show():
    st.title("Mentee Dashboard")
    st.info("Browse mentors, request sessions, and track bookings.")
    user_id = st.session_state.user["userid"]

    # Create tabs
    tabs = st.tabs(["🧑‍🏫 Browse Mentors", "📄 My Requests", "📌 Book Session", "📆 My Sessions"])

# ---------------------- 🧑‍🏫 Browse Mentors Tab ----------------------
    with tabs[0]:
        st.subheader("Browse Available Mentors")
    
        try:
            mentors = supabase.table("users").select("*").eq("role", "Mentor").execute().data
        except Exception as e:
            st.error(f"❌ Failed to load mentors: {e}")
            mentors = []
    
        if mentors:
            cols = st.columns(2)  # Two mentors per row
            for i, mentor in enumerate(mentors):
                with cols[i % 2]:
                    with st.container():
                        st.markdown("---")
                        profile_pic = mentor.get("profile_image_url") or "https://via.placeholder.com/150"
                        st.image(profile_pic, width=150, caption=mentor.get("fullname", "Mentor"))
    
                        st.markdown(f"### {mentor.get('fullname', 'Unknown')}")
                        st.markdown(f"📧 **Email:** {mentor.get('email', 'N/A')}")
                        st.markdown(f"💼 **Expertise:** {mentor.get('expertise', 'Not specified')}")
                        st.markdown(f"📝 **Bio:** {mentor.get('bio', 'No bio provided.')}")
                        st.markdown(f"🌍 **Location:** {mentor.get('location', 'Unknown')}")
    
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
                                    st.success(f"✅ Mentorship request sent to {mentor['email']}!")
                                    time.sleep(1)
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to send request: {e}")
        else:
            st.info("No mentors found at this time.")

    # ---------------------- 📄 My Requests Tab ----------------------
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

    # ---------------------- 📌 Book a Session Tab ----------------------
    with tabs[2]:
        show_booking()

    # ---------------------- 📆 My Sessions Tab ----------------------
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
                - Date: {session_date}
                - Rating: {rating}
                - Feedback: {feedback}
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
