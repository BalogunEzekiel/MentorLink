import streamlit as st
from datetime import datetime, timedelta
from database import supabase
from utils.helpers import format_datetime
from mentor_calendar import show_calendar

def show():
    st.title("Mentor Dashboard")
    st.info("View mentorship requests, manage availability, and see upcoming sessions.")

    # Ensure user is logged in
    if "user" not in st.session_state:
        st.error("Please log in first.")
        return

    user = st.session_state.user
    mentor_id = user.get("userid")

    if not mentor_id:
        st.error("Mentor ID not found.")
        return

    # Create tabs for navigation
    tabs = st.tabs(["📥 Requests", "📅 Sessions", "🗓 Calendar"])

    # 📥 Incoming Mentorship Requests Tab
    with tabs[0]:
        st.subheader("Incoming Mentorship Requests")
        requests = supabase.table("mentorshiprequest") \
            .select("*, users!mentorshiprequest_menteeid_fkey(email)") \
            .eq("mentorid", mentor_id).eq("status", "PENDING") \
            .execute().data

        if requests:
            for req in requests:
                mentee_email = req["users"]["email"]
                st.markdown(f"**From:** {mentee_email}")
                col1, col2 = st.columns(2)

                # Accept button
                if col1.button("Accept", key=f"accept_{req['mentorshiprequestid']}"):
                    # 1. Update request status
                    supabase.table("mentorshiprequest").update({"status": "ACCEPTED"}) \
                        .eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()

                    # 2. Create session (schedule for 1 day ahead by default)
                    session_date = (datetime.now() + timedelta(days=1)).isoformat()

                    supabase.table("session").insert({
                        "mentorid": req["mentorid"],
                        "menteeid": req["menteeid"],
                        "date": session_date,
                        "status": "accepted",
                        "mentorshiprequestid": req["mentorshiprequestid"]
                    }).execute()

                    st.success(f"✅ Accepted request from {mentee_email} and scheduled session.")
                    st.rerun()

                # Reject button
                if col2.button("Reject", key=f"reject_{req['mentorshiprequestid']}"):
                    supabase.table("mentorshiprequest").update({"status": "REJECTED"}) \
                        .eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()
                    st.warning(f"❌ Rejected request from {mentee_email}")
                    st.rerun()
        else:
            st.info("No pending requests.")

    # 📅 Scheduled Sessions Tab
    with tabs[1]:
        st.subheader("Scheduled Sessions")

        sessions = supabase.table("session") \
            .select("*, users!session_menteeid_fkey(email)") \
            .eq("mentorid", mentor_id) \
            .order("date", desc=False).execute().data

        if sessions:
            for s in sessions:
                st.markdown(f"""
                #### Session with {s['users']['email']}
                - 🗓 **Date:** {format_datetime(s['date'])}
                - ⭐ **Rating:** {s.get('rating', 'Pending')}
                - 💬 **Feedback:** {s.get('feedback', 'Not submitted yet')}
                """)
        else:
            st.info("No upcoming or past sessions yet.")

    # 🗓 Visual Schedule Tab
    with tabs[2]:
        st.subheader("Visual Schedule")
        show_calendar()
