# mentor.py

import streamlit as st
from datetime import datetime, timedelta
import os

from database import supabase
from utils.helpers import format_datetime_safe
from utils.session_creator import create_session_if_available
from postgrest.exceptions import APIError
from mentor_calendar import show_calendar


def show():
    st.title("Mentor Dashboard")
    st.info("Manage requests, set your availability, and track sessions.")

    if "user" not in st.session_state:
        st.error("Please log in to access the dashboard.")
        return

    mentor = st.session_state.user
    mentor_id = mentor.get("userid")

    def upload_profile_picture(file):
        if not file:
            return None

        path = f"{mentor_id}/{file.name}"
        try:
            supabase.storage.from_("profilepics").remove([path])  # Overwrite existing
            supabase.storage.from_("profilepics").upload(path, bytes(file.getbuffer()))
            return f"https://{os.getenv('SUPABASE_PROJECT_REF')}.supabase.co/storage/v1/object/public/profilepics/{path}"
        except Exception as e:
            st.error(f"Upload error: {e}")
            return None

    tabs = st.tabs(["📥 Requests", "📅 Sessions", "🗓 Availability", "🖼️ Profile Picture"])

    # ---------------------- 📥 Requests Tab ----------------------
    with tabs[0]:
        st.subheader("Incoming Mentorship Requests")

        try:
            requests = supabase.table("mentorshiprequest") \
                .select("*") \
                .eq("mentorid", mentor_id) \
                .eq("status", "PENDING") \
                .execute().data or []
        except APIError as e:
            st.error("Error fetching requests.")
            st.code(str(e))
            return

        if requests:
            mentee_ids = list({r["menteeid"] for r in requests})
            mentees = supabase.table("users").select("userid, email").in_("userid", mentee_ids).execute().data or []
            mentee_lookup = {m["userid"]: m["email"] for m in mentees}

            for req in requests:
                mentee_email = mentee_lookup.get(req["menteeid"], "Unknown")
                st.markdown(f"📨 **From:** {mentee_email}")
                col1, col2 = st.columns(2)

                if col1.button("✅ Accept", key=f"accept_{req['mentorshiprequestid']}"):
                    try:
                        supabase.table("mentorshiprequest").update(
                            {"status": "ACCEPTED"}
                        ).eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()

                        session_date = (datetime.now() + timedelta(days=1)).isoformat()
                        supabase.table("session").insert({
                            "mentorid": mentor_id,
                            "menteeid": req["menteeid"],
                            "date": session_date,
                            "mentorshiprequestid": req["mentorshiprequestid"]
                        }).execute()

                        st.success(f"Accepted request from {mentee_email} and scheduled session.")
                        st.rerun()
                    except APIError as e:
                        st.error("Failed to accept request.")
                        st.code(str(e))

                if col2.button("❌ Reject", key=f"reject_{req['mentorshiprequestid']}"):
                    try:
                        supabase.table("mentorshiprequest").update(
                            {"status": "REJECTED"}
                        ).eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()

                        st.warning(f"Rejected request from {mentee_email}")
                        st.rerun()
                    except APIError as e:
                        st.error("Failed to reject request.")
                        st.code(str(e))
        else:
            st.info("No new mentorship requests.")

    # ---------------------- 📅 Sessions Tab ----------------------
    with tabs[1]:
        st.subheader("Your Scheduled Sessions")

        try:
            sessions = supabase.table("session") \
                .select("*") \
                .eq("mentorid", mentor_id) \
                .order("date", desc=False) \
                .execute().data or []
        except APIError as e:
            st.error("Error fetching sessions.")
            st.code(str(e))
            return

        if sessions:
            mentee_ids = list({s["menteeid"] for s in sessions})
            mentees = supabase.table("users").select("userid, email").in_("userid", mentee_ids).execute().data or []
            mentee_lookup = {m["userid"]: m["email"] for m in mentees}

            for s in sessions:
                mentee_email = mentee_lookup.get(s["menteeid"], "Unknown")
                st.markdown(f"""
                #### With: {mentee_email}
                - 🗓 Date: {format_datetime_safe(s['date'])}
                - ⭐ Rating: {s.get('rating', 'Pending')}
                - 💬 Feedback: {s.get('feedback', 'Not submitted')}
                """)
        else:
            st.info("You don't have any sessions yet.")

    # ---------------------- 🗓 Availability Tab ----------------------
    with tabs[2]:
        st.subheader("Visual Availability Calendar")
        show_calendar()

        st.divider()
        st.subheader("📅 Add Availability")

        with st.form("availability_form", clear_on_submit=True):
            start_date = st.date_input("Start Date", value=datetime.now().date())
            start_time = st.time_input("Start Time", value=datetime.now().time())
            end_date = st.date_input("End Date", value=start_date)
            end_time = st.time_input("End Time", value=(datetime.now() + timedelta(hours=1)).time())

            submitted = st.form_submit_button("➕ Add Slot")
            if submitted:
                start = datetime.combine(start_date, start_time)
                end = datetime.combine(end_date, end_time)

                if end <= start:
                    st.warning("End time must be after start time.")
                else:
                    try:
                        supabase.table("availability").insert({
                            "mentorid": mentor_id,
                            "start": start.isoformat(),
                            "end": end.isoformat()
                        }).execute()
                        st.success("Availability added!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save availability: {e}")

    # ---------------------- 🖼️ Profile Picture Tab ----------------------
    with tabs[3]:
        st.subheader("Update Profile Picture")
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

        if uploaded_file:
            url = upload_profile_picture(uploaded_file)
            if url:
                try:
                    supabase.table("profile").update({
                        "profile_image_url": url
                    }).eq("userid", mentor_id).execute()
                    st.success("Profile picture updated!")
                    st.image(url, width=150)
                except Exception as e:
                    st.error(f"Failed to update profile: {e}")
