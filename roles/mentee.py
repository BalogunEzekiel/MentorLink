import streamlit as st
from database import supabase
from utils.helpers import format_datetime_safe
from utils.session_creator import create_session_if_available
from emailer import send_email
from datetime import datetime, timedelta
import pytz
import time
import uuid
from datetime import datetime
import pytz

# 🕓 Streamlit JS Eval to get local timezone
from streamlit_js_eval import streamlit_js_eval

WAT = pytz.timezone("Africa/Lagos")
now_wat = datetime.now(WAT)

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
    
        # Load all mentors
        try:
            mentors = supabase.table("users") \
                .select("*, profile(name, bio, skills, goals, profile_image_url)") \
                .eq("role", "Mentor").eq("status", "Active").execute().data or []
        except Exception as e:
            st.error(f"Failed to load mentors: {e}")
            mentors = []
    
        if not mentors:
            st.info("No mentors available.")
        else:
            # Build skill filter
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
    
            # Fetch used availability slots from session table
            try:
                matched_sessions = supabase.table("session").select("availabilityid").execute().data or []
                used_ids = {s.get("availabilityid") for s in matched_sessions if s.get("availabilityid")}
            except Exception as e:
                used_ids = set()
                st.error(f"Could not load matched sessions: {e}")
    
            now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    
            # Display mentor cards
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
    
                    # Load mentor's availability
                    try:
                        availability = supabase.table("availability") \
                            .select("availabilityid, start, end").eq("mentorid", mentor["userid"]).execute().data or []
                    except Exception as e:
                        availability = []
                        st.warning(f"Could not fetch availability for {name}: {e}")
    
                    # Filter upcoming, unmatched slots
                    upcoming_free_slots = []
                    for slot in availability:
                        availability_id = slot.get("availabilityid")
                        slot_start_str = slot.get("start")
                        slot_end_str = slot.get("end")
    
                        if not availability_id or not slot_start_str or not slot_end_str:
                            continue
    
                        try:
                            slot_start = datetime.fromisoformat(slot_start_str.replace("Z", "+00:00"))
                            slot_end = datetime.fromisoformat(slot_end_str.replace("Z", "+00:00"))
    
                            # Ensure timezone-awareness
                            if slot_start.tzinfo is None:
                                slot_start = slot_start.replace(tzinfo=pytz.utc)
                            if slot_end.tzinfo is None:
                                slot_end = slot_end.replace(tzinfo=pytz.utc)
                        except Exception as e:
                            st.warning(f"⚠️ Invalid slot datetime: {e}")
                            continue
    
                        if availability_id not in used_ids and slot_start > now_utc:
                            local_start = slot_start.astimezone()
                            local_end = slot_end.astimezone()
                            label = f"{local_start.strftime('%A %d %b %Y %I:%M %p')} ➡ {local_end.strftime('%I:%M %p')}"
                            upcoming_free_slots.append((label, availability_id))
    
                    # Show slot selector and request button
                    if upcoming_free_slots:
                        slot_labels = [label for label, _ in upcoming_free_slots]
                        slot_mapping = {label: aid for label, aid in upcoming_free_slots}
    
                        selected_slot = st.selectbox(
                            "🕒 Choose a time slot",
                            options=slot_labels,
                            key=f"slot_select_{mentor['userid']}"
                        )
    
                        if st.button("Request Mentorship", key=f"req_{mentor['userid']}"):
                            try:
                                # Check if existing request
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
                                        "status": "PENDING",
                                        "availabilityid": slot_mapping[selected_slot]
                                    }).execute()
                                    st.success(f"✅ Request sent to {mentor['email']}!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to request mentorship: {e}")
                    else:
                        st.warning("This mentor has no upcoming free slots.")

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
                .select("sessionid, rating, feedback, availability:availabilityid(start, end), users!session_mentorid_fkey(email)") \
                .eq("menteeid", user_id).execute().data or []
        except Exception as e:
            st.error(f"Could not fetch sessions for feedback: {e}")
            sessions = []
    
        now_wat = datetime.now(WAT)
        pending_feedback_sessions = []
    
        if not sessions:
            st.info("No sessions to give feedback for.")
        else:
            for session in sessions:
                mentor_email = session.get("users", {}).get("email", "Unknown")
                availability = session.get("availability", {})
                start_str = availability.get("start")
                end_str = availability.get("end")
    
                start_dt = datetime.fromisoformat(start_str) if start_str else None
                end_dt = datetime.fromisoformat(end_str) if end_str else None
    
                has_feedback = session.get("rating") and session.get("feedback")
    
                # Only prompt feedback for sessions that have expired and no feedback yet
                if end_dt and now_wat > end_dt and not has_feedback:
                    pending_feedback_sessions.append(session)
    
            if not pending_feedback_sessions:
                st.success("✅ You have completed all required feedback.")
            else:
                st.warning("⚠️ You must submit feedback for expired sessions to continue.")
                for session in pending_feedback_sessions:
                    mentor_email = session.get("users", {}).get("email", "Unknown")
                    start_str = session["availability"].get("start")
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
