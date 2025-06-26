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

    # 📥 Incoming Mentorship Requests Tab (manual join)
    with tabs[0]:
        st.subheader("Incoming Mentorship Requests")

        # 1. Get requests
        requests = supabase.table("mentorshiprequest") \
            .select("*") \
            .eq("mentorid", mentor_id).eq("status", "PENDING") \
            .execute().data

        if requests:
            # 2. Extract mentee IDs
            mentee_ids = list({r["menteeid"] for r in requests if r.get("menteeid")})

            # 3. Fetch mentees' emails
            mentees = supabase.table("users") \
                .select("userid, email") \
                .in_("userid", mentee_ids) \
                .execute().data

            # 4. Build lookup dictionary
            mentee_lookup = {m["userid"]: m["email"] for m in mentees}

            # 5. Render requests
            for req in requests:
                mentee_email = mentee_lookup.get(req["menteeid"], "Unknown")
                st.markdown(f"**From:** {mentee_email}")
                col1, col2 = st.columns(2)

                if col1.button("Accept", key=f"accept_{req['mentorshiprequestid']}"):
                    supabase.table("mentorshiprequest").update({"status": "ACCEPTED"}) \
                        .eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()

                    session_date = (datetime.now() + timedelta(days=1)).isoformat()
                try:
                    supabase.table("session").insert({
                        "mentorid": req["mentorid"],
                        "menteeid": req["menteeid"],
                        "date": session_date,
                        "status": "accepted",
                        "mentorshiprequestid": req["mentorshiprequestid"]
                    }).execute()
                except APIError as e:
                    st.error("Failed to create session.")
                    st.code(str(e), language="json")

                    st.success(f"✅ Accepted request from {mentee_email} and scheduled session.")
                    st.rerun()

                if col2.button("Reject", key=f"reject_{req['mentorshiprequestid']}"):
                    supabase.table("mentorshiprequest").update({"status": "REJECTED"}) \
                        .eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()
                    st.warning(f"❌ Rejected request from {mentee_email}")
                    st.rerun()
        else:
            st.info("No pending requests.")

    # 📅 Scheduled Sessions Tab (manual join)
    with tabs[1]:
        st.subheader("Scheduled Sessions")

        # 1. Fetch sessions for this mentor
        sessions = supabase.table("session") \
            .select("*") \
            .eq("mentorid", mentor_id) \
            .order("date", desc=False) \
            .execute().data

        if sessions:
            # 2. Get unique mentee IDs
            mentee_ids = list({s["menteeid"] for s in sessions if s.get("menteeid")})

            # 3. Fetch mentee emails
            mentees = supabase.table("users") \
                .select("userid, email") \
                .in_("userid", mentee_ids) \
                .execute().data

            # 4. Create mentee lookup dictionary
            mentee_lookup = {m["userid"]: m["email"] for m in mentees}

            # 5. Display each session with mentee email
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

    # 🗓 Visual Schedule Tab
    with tabs[2]:
        st.subheader("Visual Schedule")
        show_calendar()
