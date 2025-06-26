import streamlit as st
from datetime import datetime, timedelta
from database import supabase
from utils.helpers import format_datetime
from mentor_calendar import show_calendar
from postgrest.exceptions import APIError

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

        try:
            requests = supabase.table("mentorshiprequest") \
                .select("*") \
                .eq("mentorid", mentor_id).eq("status", "PENDING") \
                .execute().data
        except APIError as e:
            st.error("Failed to fetch mentorship requests.")
            st.code(str(e), language="json")
            return

        if requests:
            mentee_ids = list({r["menteeid"] for r in requests if r.get("menteeid")})

            try:
                mentees = supabase.table("users") \
                    .select("userid, email") \
                    .in_("userid", mentee_ids) \
                    .execute().data
            except APIError as e:
                st.error("Failed to fetch mentee details.")
                st.code(str(e), language="json")
                return

            mentee_lookup = {m["userid"]: m["email"] for m in mentees}

            for req in requests:
                mentee_email = mentee_lookup.get(req["menteeid"], "Unknown")
                st.markdown(f"**From:** {mentee_email}")
                col1, col2 = st.columns(2)

                if col1.button("Accept", key=f"accept_{req['mentorshiprequestid']}"):
                    try:
                        # Accept the mentorship request
                        supabase.table("mentorshiprequest").update({"status": "ACCEPTED"}) \
                            .eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()

                        # Schedule session 1 day later
                        session_date = (datetime.now() + timedelta(days=1)).isoformat()

                        # Insert new session
                        supabase.table("session").insert({
                            "mentorid": req["mentorid"],
                            "menteeid": req["menteeid"],
                            "date": session_date,
                            "mentorshiprequestid": req["mentorshiprequestid"]
                            # feedback and rating are now nullable — no need to insert
                        }).execute()

                        st.success(f"✅ Accepted request from {mentee_email} and scheduled session.")
                        st.rerun()
                    except APIError as e:
                        st.error("Failed to accept and schedule session.")
                        st.code(str(e), language="json")

                if col2.button("Reject", key=f"reject_{req['mentorshiprequestid']}"):
                    try:
                        supabase.table("mentorshiprequest").update({"status": "REJECTED"}) \
                            .eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()
                        st.warning(f"❌ Rejected request from {mentee_email}")
                        st.rerun()
                    except APIError as e:
                        st.error("Failed to reject request.")
                        st.code(str(e), language="json")
        else:
            st.info("No pending requests.")

    # 📅 Scheduled Sessions Tab
    with tabs[1]:
        st.subheader("Scheduled Sessions")

        try:
            sessions = supabase.table("session") \
                .select("*") \
                .eq("mentorid", mentor_id) \
                .order("date", desc=False) \
                .execute().data
        except APIError as e:
            st.error("Failed to fetch sessions.")
            st.code(str(e), language="json")
            return

        if sessions:
            mentee_ids = list({s["menteeid"] for s in sessions if s.get("menteeid")})
            try:
                mentees = supabase.table("users") \
                    .select("userid, email") \
                    .in_("userid", mentee_ids) \
                    .execute().data
                mentee_lookup = {m["userid"]: m["email"] for m in mentees}
            except APIError as e:
                st.error("Failed to fetch mentee details.")
                st.code(str(e), language="json")
                return

            for s in sessions:
                mentee_email = mentee_lookup.get(s["menteeid"], "Unknown")
                st.markdown(f"""
                #### Session with {mentee_email}
                - 🗓 **Date:** {format_datetime(s['date'])}
                - ⭐ **Rating:** {s.get('rating', 'Pending')}
                - 💬 **Feedback:** {s.get('feedback', 'Not submitted yet')}
                """)
        else:
            st.info("No upcoming or past sessions yet.")

    # 🗓 Calendar View Tab
    with tabs[2]:
        st.subheader("Visual Schedule")
        show_calendar()
