import streamlit as st
from datetime import datetime, timedelta
from database import supabase
from utils.helpers import format_datetime
from mentor_calendar import show_calendar
from postgrest.exceptions import APIError
import os

def show():
    st.title("Mentor Dashboard")
    st.info("View mentorship requests, manage availability, and see upcoming sessions.")

    if "user" not in st.session_state:
        st.error("Please log in first.")
        return

    user = st.session_state.user
    mentor_id = user.get("userid")

    if not mentor_id:
        st.error("Mentor ID not found.")
        return

    # --- Upload profile image helper ---
    def upload_profile_picture(file):
        if file is None:
            return None
    
        file_path = f"{mentor_id}/{file.name}"
    
        try:
            # Step 1: Delete the file first if it already exists
            supabase.storage.from_("profilepics").remove([file_path])
    
            # Step 2: Upload the file (converted to bytes)
            res = supabase.storage.from_("profilepics").upload(
                file_path,
                bytes(file.getbuffer())
            )
    
            # Step 3: Build public URL manually
            public_url = (
                f"https://{os.getenv('SUPABASE_PROJECT_REF')}.supabase.co/storage/v1/object/public/profilepics/{file_path}"
            )
            return public_url
    
        except Exception as e:
            st.error(f"❌ Upload error: {e}")
            return None

    # Tabs
    tabs = st.tabs(["📥 Requests", "📅 Sessions", "🗓 Calendar", "🖼️ Profile Picture"])

    # 📥 Incoming Requests
    with tabs[0]:
        st.subheader("Incoming Mentorship Requests")
        try:
            requests = (
                supabase.table("mentorshiprequest")
                .select("*")
                .eq("mentorid", mentor_id)
                .eq("status", "PENDING")
                .execute()
                .data
            )
        except APIError as e:
            st.error("Failed to fetch mentorship requests.")
            st.code(str(e), language="json")
            return

        if requests:
            mentee_ids = list({r["menteeid"] for r in requests if r.get("menteeid")})
            try:
                mentees = (
                    supabase.table("users")
                    .select("userid, email")
                    .in_("userid", mentee_ids)
                    .execute()
                    .data
                )
                mentee_lookup = {m["userid"]: m["email"] for m in mentees}
            except APIError as e:
                st.error("Failed to fetch mentee details.")
                st.code(str(e), language="json")
                return

            for req in requests:
                mentee_email = mentee_lookup.get(req["menteeid"], "Unknown")
                st.markdown(f"**From:** {mentee_email}")
                col1, col2 = st.columns(2)

                if col1.button("Accept", key=f"accept_{req['mentorshiprequestid']}"):
                    try:
                        supabase.table("mentorshiprequest").update(
                            {"status": "ACCEPTED"}
                        ).eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()

                        session_date = (datetime.now() + timedelta(days=1)).isoformat()

                        supabase.table("session").insert({
                            "mentorid": req["mentorid"],
                            "menteeid": req["menteeid"],
                            "date": session_date,
                            "mentorshiprequestid": req["mentorshiprequestid"]
                        }).execute()

                        st.success(f"✅ Accepted request from {mentee_email} and scheduled session.")
                        st.rerun()
                    except APIError as e:
                        st.error("Failed to accept and schedule session.")
                        st.code(str(e), language="json")

                if col2.button("Reject", key=f"reject_{req['mentorshiprequestid']}"):
                    try:
                        supabase.table("mentorshiprequest").update(
                            {"status": "REJECTED"}
                        ).eq("mentorshiprequestid", req["mentorshiprequestid"]).execute()
                        st.warning(f"❌ Rejected request from {mentee_email}")
                        st.rerun()
                    except APIError as e:
                        st.error("Failed to reject request.")
                        st.code(str(e), language="json")
        else:
            st.info("No pending requests.")

    # 📅 Scheduled Sessions
    with tabs[1]:
        st.subheader("Scheduled Sessions")
        try:
            sessions = (
                supabase.table("session")
                .select("*")
                .eq("mentorid", mentor_id)
                .order("date", desc=False)
                .execute()
                .data
            )
        except APIError as e:
            st.error("Failed to fetch sessions.")
            st.code(str(e), language="json")
            return

        if sessions:
            mentee_ids = list({s["menteeid"] for s in sessions if s.get("menteeid")})
            try:
                mentees = (
                    supabase.table("users")
                    .select("userid, email")
                    .in_("userid", mentee_ids)
                    .execute()
                    .data
                )
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

    # 🗓 Calendar View
    with tabs[2]:
    st.subheader("Visual Schedule")
    show_calendar()

    st.divider()
    st.subheader("📅 Set Your Availability")

    with st.form("set_availability_form", clear_on_submit=True):
        start = st.datetime_input("Start Time", value=datetime.now() + timedelta(hours=1))
        end = st.datetime_input("End Time", value=datetime.now() + timedelta(hours=2))

        submitted = st.form_submit_button("➕ Add Availability")
        if submitted:
            if end <= start:
                st.error("❌ End time must be after start time.")
            else:
                try:
                    supabase.table("availability").insert({
                        "mentorid": mentor_id,
                        "start": start.isoformat(),
                        "end": end.isoformat()
                    }).execute()
                    st.success("✅ Availability added successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to save availability: {e}")

    # 🖼️ Profile Picture Tab
    with tabs[3]:
        st.subheader("Upload or Update Your Profile Picture")

        uploaded_file = st.file_uploader("Choose a profile picture", type=["png", "jpg", "jpeg"])

        if uploaded_file:
            image_url = upload_profile_picture(uploaded_file)
            if image_url:
                try:
                    supabase.table("profile").update({
                        "profile_image_url": image_url
                    }).eq("userid", mentor_id).execute()
                    st.success("✅ Profile picture updated!")
                    st.image(image_url, width=150)
                except Exception as e:
                    st.error(f"❌ Failed to update profile: {e}")
