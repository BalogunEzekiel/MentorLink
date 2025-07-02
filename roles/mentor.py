import streamlit as st
from database import supabase
from datetime import datetime, timedelta
from utils.helpers import format_datetime_safe
from utils.session_creator import create_session_with_meet_and_email
from emailer import send_email


def show():
    st.title("Mentor Dashboard")
    st.info("Manage your sessions, availability, profile, and mentorship requests.")
    mentor_id = st.session_state.user["userid"]

    tabs = st.tabs([
        "🏠 Dashboard",
        "📅 My Sessions",
        "📌 Add Availability",
        "📥 Requests"
    ])

    # ---------------------- 🏠 Dashboard Tab ----------------------
    with tabs[0]:
        st.subheader("Welcome to your Mentor Dashboard")

        profile_data = supabase.table("profile").select("*").eq("userid", mentor_id).execute().data
        profile = profile_data[0] if profile_data else {}

        # Summary
        st.markdown("### 📊 Summary")
        total_requests = supabase.table("mentorshiprequest").select("mentorshiprequestid").eq("mentorid", mentor_id).execute().data
        total_sessions = supabase.table("session").select("sessionid").eq("mentorid", mentor_id).execute().data

        st.write(f"- 📥 Incoming Requests: **{len(total_requests)}**")
        st.write(f"- 📅 Total Sessions: **{len(total_sessions)}**")

        # Profile Management
        st.markdown("### 🙍‍♂️ Update Profile")
        with st.form("mentor_profile_form"):
            name = st.text_input("Name", value=profile.get("name", ""))
            bio = st.text_area("Bio", value=profile.get("bio", ""))
            skills = st.text_area("Skills", value=profile.get("skills", ""))
            goals = st.text_area("Goals", value=profile.get("goals", ""))
            profile_image = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])

            submit_btn = st.form_submit_button("Update Profile")

            if submit_btn:
                update_data = {
                    "userid": mentor_id,
                    "name": name,
                    "bio": bio,
                    "skills": skills,
                    "goals": goals,
                }

                if profile_image:
                    avatar_url = f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&size=256"
                    update_data["profile_image_url"] = avatar_url

                supabase.table("profile").upsert(update_data, on_conflict=["userid"]).execute()
#                supabase.table("profile").upsert(update_data).execute()
                st.success("✅ Profile updated successfully!")
                st.rerun()

    # ---------------------- 📅 My Sessions Tab ----------------------
    with tabs[1]:
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
                meet_link = s.get("meet_link", "#")

                st.markdown(f"""
                #### With: {mentee_email}
                - 📅 Date: {session_date}
                - ⭐ Rating: {rating}
                - 💬 Feedback: {feedback}
                - 🔗 [Join Meet]({meet_link})
                """)

                if st.button("📧 Send Reminder", key=f"reminder_{s['sessionid']}"):
                    if send_email(
                        to_email=mentee_email,
                        subject="📅 Mentorship Session Reminder",
                        body=f"This is a reminder for your session scheduled on {session_date}.\n\nJoin via Meet: {meet_link}"
                    ):
                        st.success("Reminder email sent!")
                    else:
                        st.error("Failed to send reminder.")
        else:
            st.info("No sessions yet.")

    # ---------------------- 📌 Add Availability Tab ----------------------
    with tabs[2]:
        st.subheader("Add Availability Slot")

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
                        st.success(f"Availability added: {format_datetime_safe(start)} ➡ {format_datetime_safe(end)}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add availability: {e}")

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

    # ---------------------- 📥 Requests Tab ----------------------
    with tabs[3]:
        st.subheader("Incoming Mentorship Requests")

        requests = supabase.table("mentorshiprequest") \
            .select("*, mentee:users!mentorshiprequest_menteeid_fkey(email)") \
            .eq("mentorid", mentor_id) \
            .eq("status", "PENDING").execute().data or []

        if not requests:
            st.info("No pending requests.")
        else:
            for req in requests:
                mentee_email = req.get("mentee", {}).get("email", "Unknown")
                req_id = req["mentorshiprequestid"]
                mentee_id = req["menteeid"]

                with st.expander(f"Request from {mentee_email}"):
                    col1, col2 = st.columns(2)
                    if col1.button("✅ Accept", key=f"accept_{req_id}"):
                        now = datetime.utcnow()
                        start = now + timedelta(minutes=5)
                        end = start + timedelta(minutes=30)

                        success, msg = create_session_with_meet_and_email(
                            supabase, mentor_id, mentee_id, start, end
                        )

                        if success:
                            supabase.table("mentorshiprequest").update({"status": "ACCEPTED"}) \
                                .eq("mentorshiprequestid", req_id).execute()
                            st.success("Request accepted and session booked!")
                            st.rerun()
                        else:
                            st.error(msg)

                    if col2.button("❌ Reject", key=f"reject_{req_id}"):
                        supabase.table("mentorshiprequest").update({"status": "REJECTED"}) \
                            .eq("mentorshiprequestid", req_id).execute()
                        st.info("Request rejected.")
                        st.rerun()
