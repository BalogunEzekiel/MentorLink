# roles/mentor.py

import streamlit as st
from database import supabase
from datetime import datetime, timedelta
from utils.helpers import format_datetime_safe
from utils.session_creator import create_session_with_meet_and_email
from emailer import send_email
import uuid
import pytz

WAT = pytz.timezone("Africa/Lagos")

def parse_datetime_safe(dt):
    if isinstance(dt, datetime):
        return dt.astimezone(WAT)
    if isinstance(dt, str):
        try:
            return datetime.fromisoformat(dt).astimezone(WAT)
        except ValueError:
            return None
    return None

def classify_session(start_time_str, end_time_str):
    now = datetime.now(WAT)
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

def show():
    st.title("Mentor Dashboard")
    st.info("Manage your sessions, availability, profile, and mentorship requests.")
    mentor_id = st.session_state.user["userid"]

    tabs = st.tabs([
        "🏠 Dashboard",
        "📌 Availability",
        "📥 Requests",
        "📅 Sessions"
    ])

    # --- Dashboard Tab ---
    with tabs[0]:
    
        # Create vertical menu on the left
        col1, col2 = st.columns([1, 4])
    
        with col1:
            summary_btn = st.button("📊 Summary")
            profile_btn = st.button("🙍‍♂️ Update Profile")
            inbox_btn = st.button("📥 Inbox")
    
        # Session state to track sub-tab
        if "mentor_sub_tab" not in st.session_state:
            st.session_state.mentor_sub_tab = "📊 Summary"
    
        if summary_btn:
            st.session_state.mentor_sub_tab = "📊 Summary"
        elif profile_btn:
            st.session_state.mentor_sub_tab = "🙍‍♂️ Profile"
        elif inbox_btn:
            st.session_state.mentor_sub_tab = "📥 Inbox"
    
        with col2:
            sub_tab = st.session_state.mentor_sub_tab
    
            # Fetch profile and stats
            profile_data = supabase.table("profile").select("*").eq("userid", mentor_id).execute().data
            profile = profile_data[0] if profile_data else {}
    
            total_requests = supabase.table("mentorshiprequest").select("mentorshiprequestid").eq("mentorid", mentor_id).execute().data or []
            total_sessions = supabase.table("session").select("sessionid").eq("mentorid", mentor_id).execute().data or []
    
            if sub_tab == "📊 Summary":
                st.markdown("### 📊 Summary")
                st.write(f"- 📥 Incoming Requests: **{len(total_requests)}**")
                st.write(f"- 📅 Total Sessions: **{len(total_sessions)}**")
    
            elif sub_tab == "🙍‍♂️ Update Profile":
                st.markdown("### 🙍‍♂️ Update Profile")
            
                if profile.get("profile_image_url"):
                    st.image(profile["profile_image_url"], width=100, caption="Current Profile Picture")
            
                with st.form("mentor_profile_form"):
                    name = st.text_input("Name", value=profile.get("name", ""))
                    bio = st.text_area("Bio", value=profile.get("bio", ""))
                    skills = st.text_area("Skills", value=profile.get("skills", ""))
                    goals = st.text_area("Goals", value=profile.get("goals", ""))
                    profile_image = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
            
                    if st.form_submit_button("Update Profile"):
                        update_data = {
                            "userid": mentor_id,
                            "name": name,
                            "bio": bio,
                            "skills": skills,
                            "goals": goals,
                        }
            
                        if profile_image:
                            try:
                                file_ext = profile_image.type.split("/")[-1]
                                file_name = f"{mentor_id}_{uuid.uuid4()}.{file_ext}"
                                file_bytes = profile_image.getvalue()
                                supabase.storage.from_("profilepics").upload(file_name, file_bytes)
                                public_url = supabase.storage.from_("profilepics").get_public_url(file_name)
                                update_data["profile_image_url"] = public_url
                            except Exception as e:
                                st.error(f"Profile image upload failed: {e}")
            
                        try:
                            response = supabase.table("profile").upsert(update_data, on_conflict=["userid"]).execute()
                            st.success("✅ Profile updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to update profile: {e}")
                            st.write("Supabase response:", response)

                        
            elif sub_tab == "📥 Inbox":
                st.subheader("📥 Inbox")
            
                user_role = st.session_state.get("user_role")
                user_id = st.session_state.get("user_id")
            
                if not user_id:
                    st.warning("⚠️ User ID not found in session. Please log in again.")
                else:
                    try:
                        messages = supabase.table("messages") \
                            .select("*") \
                            .or_(f"receiver_id.eq.{user_id},role.eq.{user_role},role.is.null") \
                            .order("created_at", desc=True) \
                            .execute().data or []
            
                        unread_count = sum(not m["is_read"] for m in messages)
                        st.markdown(f"🔔 Unread Messages: **{unread_count}**")
            
                        for msg in messages:
                            with st.expander(f"{'📨' if not msg['is_read'] else '📄'} {msg['title']} ({msg['created_at'][:16]})"):
                                st.write(msg["body"])
                                if not msg["is_read"]:
                                    supabase.table("messages").update({"is_read": True}).eq("id", msg["id"]).execute()
            
                    except Exception as e:
                        st.error(f"❌ Failed to load messages: {e}")
######
    
            elif sub_tab == "📥 Inbox":
                st.subheader("📥 Inbox")
    
                user_role = st.session_state.get("user_role")
                user_id = st.session_state.get("user_id")
    
                try:
                    messages = supabase.table("messages") \
                        .select("*") \
                        .or_(f"receiver_id.eq.{user_id},role.eq.{user_role},role.is.null") \
                        .order("created_at", desc=True) \
                        .execute().data or []
    
                    unread_count = sum(not m["is_read"] for m in messages)
                    st.markdown(f"🔔 Unread Messages: **{unread_count}**")
    
                    for msg in messages:
                        with st.expander(f"{'📨' if not msg['is_read'] else '📄'} {msg['title']} ({msg['created_at'][:16]})"):
                            st.write(msg["body"])
                            if not msg["is_read"]:
                                supabase.table("messages").update({"is_read": True}).eq("id", msg["id"]).execute()
    
                except Exception as e:
                    st.error(f"❌ Failed to load messages: {e}")
                
    # --- Availability Tab ---
    with tabs[1]:
        st.subheader("Add Availability Slot")
    
        # Fetch slots early so it's available for overlap checks
        slots = supabase.table("availability").select("*").eq("mentorid", mentor_id).execute().data or []
    
        # Fetch all sessions and build a set of used availabilityids
        try:
            session_records = supabase.table("session").select("availabilityid").execute().data or []
            used_availability_ids = {s["availabilityid"] for s in session_records if s.get("availabilityid")}
        except Exception as e:
            used_availability_ids = set()
            st.error(f"Failed to fetch session data: {e}")
    
        with st.form(f"availability_form_{mentor_id}", clear_on_submit=True):
            now_wat = datetime.now(WAT)
    
            date = st.date_input("Date", value=now_wat.date())
            start_time = st.time_input("Start Time")
            end_time = st.time_input("End Time")
            submitted = st.form_submit_button("➕ Add Slot")
    
            if submitted:
                start = datetime.combine(date, start_time).replace(tzinfo=WAT)
                end = datetime.combine(date, end_time).replace(tzinfo=WAT)
    
                if end <= start:
                    st.warning("End time must be after start time.")
                else:
                    availability_date = date.isoformat()
    
                    overlapping = [
                        s for s in slots
                        if not (end <= datetime.fromisoformat(s["start"]) or start >= datetime.fromisoformat(s["end"]))
                    ]
    
                    if overlapping:
                        st.warning("⛔ This slot overlaps with an existing one. Please choose a different time.")
                    else:
                        try:
                            supabase.table("availability").insert({
                                "mentorid": mentor_id,
                                "start": start.isoformat(),
                                "end": end.isoformat(),
                                "date": availability_date
                            }).execute()
                            st.success(f"Availability added: {format_datetime_safe(start)} ➡ {format_datetime_safe(end)}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to add availability: {e}")
    
        st.markdown("### Existing Availability")
    
        if slots:
            for slot in slots:
                availability_id = slot.get("availabilityid")
                start = format_datetime_safe(slot.get("start"), tz=WAT)
                end = format_datetime_safe(slot.get("end"), tz=WAT)
    
                is_used = availability_id in used_availability_ids
                status_text = "✅ Matched" if is_used else "🟢 Available"
    
                col1, col2 = st.columns([6, 1])
                col1.markdown(f"- 🕒 {start} ➡ {end} &nbsp;&nbsp; **{status_text}**")
    
                if not is_used:
                    if col2.button("❌", key=f"delete_slot_{availability_id}"):
                        try:
                            supabase.table("availability").delete().eq("availabilityid", availability_id).execute()
                            st.success("Availability removed.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to remove slot: {e}")
                else:
                    col2.markdown("🔒")
        else:
            st.info("No availability slots added yet.")

####
    # --- Requests Tab ---
    with tabs[2]:
        st.subheader("Incoming Mentorship Requests")
        requests = supabase.table("mentorshiprequest") \
            .select("*, mentee:users!mentorshiprequest_menteeid_fkey(email, userid)") \
            .eq("mentorid", mentor_id).eq("status", "PENDING").execute().data or []
    
        if not requests:
            st.info("No pending requests.")
        else:
            for req in requests:
                mentee = req.get("mentee", {})
                mentee_email = mentee.get("email", "Unknown")
                mentee_id = mentee.get("userid")
                req_id = req["mentorshiprequestid"]
    
                mentee_profile_data = supabase.table("profile").select("*").eq("userid", mentee_id).execute().data
                mentee_profile = mentee_profile_data[0] if mentee_profile_data else {}
    
                with st.expander(f"Request from {mentee_email}"):
                    if mentee_profile.get("profile_image_url"):
                        st.image(mentee_profile["profile_image_url"], width=100)
    
                    st.markdown(f"""
                    **Name:** {mentee_profile.get("name", "N/A")}  
                    **Bio:** {mentee_profile.get("bio", "N/A")}  
                    **Skills:** {mentee_profile.get("skills", "N/A")}  
                    **Goals:** {mentee_profile.get("goals", "N/A")}
                    """)
    
                    try:
                        # Get all unused slots for this mentor
                        all_slots = supabase.table("availability").select("*").eq("mentorid", mentor_id).execute().data or []
                        used_sessions = supabase.table("session").select("availabilityid").execute().data or []
                        used_ids = {s["availabilityid"] for s in used_sessions if s.get("availabilityid")}
                        available_slots = [s for s in all_slots if s["availabilityid"] not in used_ids]
    
                        if available_slots:
                            first_slot = available_slots[0]  # Automatically use first available slot
    
                            if st.button("✅ Accept and Book Slot", key=f"accept_{req_id}"):
                                try:
                                    supabase.table("session").insert({
                                        "mentorid": mentor_id,
                                        "menteeid": mentee_id,
                                        "mentorshiprequestid": req_id,
                                        "availabilityid": first_slot["availabilityid"],
                                        "date": first_slot.get("date")
                                    }).execute()
    
                                    supabase.table("mentorshiprequest").update({"status": "ACCEPTED"}) \
                                        .eq("mentorshiprequestid", req_id).execute()
    
                                    st.success("✅ Request accepted and session booked!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Failed to save session to database: {e}")
                        else:
                            st.warning("❌ No available slots to schedule a session.")
    
                    except Exception as e:
                        st.error(f"❌ Error checking availability: {e}")
    
                    if st.button("❌ Reject", key=f"reject_{req_id}"):
                        supabase.table("mentorshiprequest").update({"status": "REJECTED"}) \
                            .eq("mentorshiprequestid", req_id).execute()
                        st.info("Request rejected.")
                        st.rerun()

    # --- Sessions Tab ---
    with tabs[3]:
        st.subheader("🧑‍🏫 Your Mentorship Sessions")
    
        # Load all sessions for this mentor
        sessions = supabase.table("session").select("*, users!session_menteeid_fkey(email)") \
            .eq("mentorid", mentor_id).execute().data or []
    
        # Load all availability records for this mentor
        availability_records = supabase.table("availability").select("*") \
            .eq("mentorid", mentor_id).execute().data or []
    
        # Create a lookup dict: availability_id → (start, end)
        availability_map = {
            a["availabilityid"]: (a.get("start"), a.get("end")) for a in availability_records
        }
    
        if sessions:
            for s in sessions:
                mentee_email = s.get("users", {}).get("email", "Unknown")
                start_str = s.get("start")
                end_str = s.get("end")
    
                # ✅ Use availability slot if start or end is missing
                availability_id = s.get("availabilityid")
                if (not start_str or not end_str) and availability_id in availability_map:
                    start_str, end_str = availability_map[availability_id]
    
                start_fmt = format_datetime_safe(start_str, tz=WAT) if start_str else "❌ Missing"
                end_fmt = format_datetime_safe(end_str, tz=WAT) if end_str else "❌ Missing"
    
                meet_link = s.get("meet_link", "#")
                status, emoji = classify_session(start_str, end_str)
    
                st.markdown(f"""
                ### {emoji} {status} Session
                - 👤 With: **{mentee_email}**
                - 🕒 Start: {start_fmt}
                - 🕔 End: {end_fmt}
                - 🔗 [Join Meet]({meet_link})
                """)
    
                if st.button("📧 Send Reminder", key=f"reminder_{s['sessionid']}"):
                    if send_email(
                        to_email=mentee_email,
                        subject="📅 Mentorship Session Reminder",
                        body=f"This is a reminder for your session scheduled on {start_fmt}.\n\nJoin via Meet: {meet_link}"
                    ):
                        st.success("Reminder email sent!")
                    else:
                        st.error("Failed to send reminder.")
        else:
            st.info("No mentorship sessions yet.")
