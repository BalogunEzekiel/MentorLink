import streamlit as st
from database import supabase
from utils.helpers import format_datetime_safe
from utils.session_creator import create_session_if_available
from emailer import send_email
from datetime import datetime, timedelta
import pytz
import time
import uuid

# 🕓 Streamlit JS Eval to get local timezone
from streamlit_js_eval import streamlit_js_eval

WAT = pytz.timezone("Africa/Lagos")

def classify_session(start_time_str, end_time_str):
    now = datetime.now(WAT)

    def parse_datetime_safe(dt):
        if isinstance(dt, datetime):
            return dt.astimezone(WAT)
        if isinstance(dt, str):
            try:
                return datetime.fromisoformat(dt).astimezone(WAT)
            except ValueError:
                pass
        return None

    start = parse_datetime_safe(start_time_str)
    end = parse_datetime_safe(end_time_str)

    if not start or not end:
        return "Invalid", "❌"
    if end < now:
        return "Past", "🟥"
    elif start <= now <= end:
        return "Ongoing", "🟨"
    else:
        return "Upcoming", "🟩"

def convert_to_user_timezone(dt_string, user_tz_str):
    try:
        dt_obj = datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        if dt_obj.tzinfo is None:
            dt_obj = pytz.utc.localize(dt_obj)
        user_tz = pytz.timezone(user_tz_str)
        return dt_obj.astimezone(user_tz).strftime("%A, %d %B %Y at %I:%M %p")
    except Exception:
        return "❌ Invalid Date"

def show():
    if "mentor_request_success_message" in st.session_state:
        st.success(st.session_state.pop("mentor_request_success_message"))

    st.title("Mentee Dashboard")
    st.info("Browse mentors, request sessions, track bookings, and give feedback.")

    # 🧑 Get user ID from session
    user = st.session_state.get("user")
    user_id = user.get("userid") if user and isinstance(user, dict) else None

    if not user_id:
        st.error("⚠️ User session not found or invalid. Please log in again.")
        st.stop()

    # 🌍 Get mentee's local timezone from browser
    mentee_timezone = streamlit_js_eval(js_expressions="Intl.DateTimeFormat().resolvedOptions().timeZone", key="tz") or "Africa/Lagos"

    tabs = st.tabs([
        "🏠 Dashboard",
        "🧑‍🏫 Browse Mentors",
        "📄 My Requests",
        "📆 My Sessions",
        "✅ Session Feedback"
    ])
    
    # --- Dashboard Tab ---
    with tabs[0]:
        st.subheader("Welcome to your Mentee Dashboard")
        try:
            profile_data = supabase.table("profile").select("*").eq("userid", user_id).execute().data
            profile = profile_data[0] if profile_data else {}

            total_requests = supabase.table("mentorshiprequest").select("mentorshiprequestid").eq("menteeid", user_id).execute().data or []
            total_sessions = supabase.table("session").select("sessionid").eq("menteeid", user_id).execute().data or []
        except Exception as e:
            st.error(f"🚫 Failed to fetch profile or summary data: {e}")
            return

        st.markdown("### 📊 Summary")
        st.write(f"- 📥 Sent Requests: **{len(total_requests)}**")
        st.write(f"- 📅 Sessions Booked: **{len(total_sessions)}**")

        st.markdown("### 🙍‍♀️ Update Profile")
        avatar_url = profile.get("profile_image_url") or f"https://ui-avatars.com/api/?name={profile.get('name', 'Mentee').replace(' ', '+')}&size=128"
        st.image(avatar_url, width=100, caption=profile.get("name", "Your Profile"))

        with st.form("mentee_profile_form"):
            name = st.text_input("Name", value=profile.get("name", ""))
            bio = st.text_area("Bio", value=profile.get("bio", ""))
            skills = st.text_area("Skills", value=profile.get("skills", ""))
            goals = st.text_area("Goals", value=profile.get("goals", ""))
            profile_image = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
            submit_btn = st.form_submit_button("Update Profile")

            if submit_btn:
                update_data = {
                    "userid": user_id,
                    "name": name,
                    "bio": bio,
                    "skills": skills,
                    "goals": goals,
                }

                if profile_image:
                    file_extension = profile_image.name.split(".")[-1]
                    file_name = f"{user_id}_{uuid.uuid4()}.{file_extension}"
                    try:
                        file_bytes = profile_image.getvalue()
                        supabase.storage.from_("profilepics").upload(
                            path=file_name,
                            file=file_bytes,
                            file_options={"content-type": profile_image.type, "x-upsert": "true"}
                        )
                        public_url = supabase.storage.from_("profilepics").get_public_url(file_name)
                        update_data["profile_image_url"] = public_url
                    except Exception as e:
                        st.warning(f"❗ Image upload failed: {e}")
                        update_data["profile_image_url"] = f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&size=256"

                try:
                    supabase.table("profile").upsert(update_data, on_conflict=["userid"]).execute()
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update profile: {e}")

    # --- Browse Mentors Tab ---
    with tabs[1]:
        st.subheader("Browse Available Mentors")
        try:
            mentors = supabase.table("users").select("*, profile(name, bio, skills, goals, profile_image_url)") \
                .eq("role", "Mentor").eq("status", "Active").execute().data or []
        except Exception as e:
            st.error(f"Failed to load mentors: {e}")
            mentors = []

        if not mentors:
            st.info("No mentors available.")
        else:
            all_skills = []
            for mentor in mentors:
                skills = mentor.get("profile", {}).get("skills", "")
                if skills:
                    all_skills.extend([skill.strip().lower() for skill in skills.split(",")])
            unique_skills = sorted(set(all_skills))
            selected_skill = st.selectbox("🎯 Filter by Skill", ["All"] + unique_skills)

            if selected_skill != "All":
                mentors = [
                    m for m in mentors
                    if selected_skill.lower() in (m.get("profile", {}).get("skills", "").lower())
                ]

            cols = st.columns(2)
            for i, mentor in enumerate(mentors):
                col = cols[i % 2]
                with col:
                    profile = mentor.get("profile") or {}
                    name = profile.get("name", "Unnamed Mentor")
                    avatar_url = profile.get("profile_image_url") or f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&size=128"
                    bio = profile.get("bio", "No bio")
                    skills = profile.get("skills", "Not listed")
                    goals = profile.get("goals", "Not set")

                    st.image(avatar_url, width=120, caption=name)
                    st.markdown(f"**Bio:** {bio}  \n**Skills:** {skills}  \n**Goals:** {goals}")

                    availability = supabase.table("availability") \
                        .select("availabilityid").eq("mentorid", mentor["userid"]).execute().data or []

                    if availability:
                        if st.button("Request Mentorship", key=f"req_{mentor['userid']}"):
                            existing = supabase.table("mentorshiprequest") \
                                .select("mentorshiprequestid", "status") \
                                .eq("menteeid", user_id).eq("mentorid", mentor["userid"]) \
                                .in_("status", ["PENDING", "ACCEPTED"]).execute().data

                            if existing:
                                st.warning("❗ You already have a pending or accepted request with this mentor.")
                                time.sleep(1)
                                st.rerun()
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

    # --- My Requests Tab ---
    with tabs[2]:
        st.subheader("Your Mentorship Requests")
        try:
            requests = supabase.table("mentorshiprequest") \
                .select("*, users!mentorshiprequest_mentorid_fkey(email)") \
                .eq("menteeid", user_id).neq("status", "ACCEPTED").execute().data or []
        except Exception as e:
            st.error(f"Could not fetch requests: {e}")
            requests = []

        if requests:
            for req in requests:
                mentor_email = req.get("users", {}).get("email", "Unknown")
                status = req.get("status", "Unknown")
                st.markdown(f"- 🧑 Mentor: **{mentor_email}**\n- 📌 Status: **{status}**")
        else:
            st.info("You have not made any mentorship requests yet.")

    # --- My Sessions Tab ---
    with tabs[3]:
        st.subheader("Your Mentorship Sessions")
        try:
            sessions = supabase.table("session") \
                .select("sessionid, rating, feedback, meet_link, availability:availabilityid(start, end), users!session_menteeid_fkey(email)") \
                .eq("menteeid", user_id).execute().data or []
        except Exception as e:
            st.error(f"Could not fetch sessions: {e}")
            sessions = []

        if sessions:
            for s in sessions:
                mentor_email = s.get("users", {}).get("email", "Unknown")
                availability = s.get("availability") or {}
                start_str = availability.get("start")
                end_str = availability.get("end")
                rating = s.get("rating", "Pending")
                feedback = s.get("feedback", "Not submitted")
                meet_link = s.get("meet_link", "#")
                status, emoji = classify_session(start_str, end_str)
                start_fmt = format_datetime_safe(start_str, tz=WAT) if start_str else "N/A"
                end_fmt = format_datetime_safe(end_str, tz=WAT) if end_str else "N/A"

                st.markdown(f"""
                    ### {emoji} {status} Session
                    - 👤 With: **{mentor_email}**
                    - 🕒 Start: {start_fmt}
                    - 🕔 End: {end_fmt}
                    - ⭐ Rating: {rating}
                    - 💬 Feedback: {feedback}
                    - 🔗 [Join Meet]({meet_link})
                """)

                if st.button("📧 Send Reminder", key=f"reminder_{s['sessionid']}"):
                    if send_email(
                        to_email=mentor_email,
                        subject="📅 Session Reminder",
                        body=f"Reminder for your session on {start_fmt}. Join via Meet: {meet_link}"
                    ):
                        st.success("Reminder email sent!")
                    else:
                        st.error("Failed to send email.")
        else:
            st.info("You don’t have any sessions yet.")

    # --- Feedback Tab ---
    with tabs[4]:
        st.subheader("Rate Mentors & Provide Feedback")
        try:
            sessions = supabase.table("session") \
                .select("sessionid, rating, feedback, availability:availabilityid(start), users!session_mentorid_fkey(email)") \
                .eq("menteeid", user_id).execute().data or []
        except Exception as e:
            st.error(f"Could not fetch sessions for feedback: {e}")
            sessions = []

        if not sessions:
            st.info("No sessions to give feedback for.")
        else:
            for session in sessions:
                if session.get("rating") and session.get("feedback"):
                    continue

                mentor_email = session.get("users", {}).get("email", "Unknown")
                availability = session.get("availability")
                start_str = availability.get("start") if availability else None
                date_str = format_datetime_safe(start_str, tz=WAT) if start_str else "Unavailable"

                with st.expander(f"Session with {mentor_email} on {date_str}"):
                    rating = st.selectbox("Rating", [1, 2, 3, 4, 5], key=f"rating_{session['sessionid']}")
                    feedback = st.text_area("Feedback", key=f"feedback_{session['sessionid']}")

                    if st.button("Submit Feedback", key=f"submit_feedback_{session['sessionid']}"):
                        try:
                            supabase.table("session").update({
                                "rating": rating,
                                "feedback": feedback
                            }).eq("sessionid", session["sessionid"]).execute()
                            st.success("Feedback submitted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error submitting feedback: {e}")
