import sys
import os
import time
from datetime import datetime
import streamlit as st
import pandas as pd
import pytz

# Adjust path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import supabase
from auth.auth_handler import register_user
from utils.session_creator import create_session_if_available
from utils.helpers import format_datetime_safe  # Handles timezone-safe formatting

# Set West Africa Time
WAT = pytz.timezone("Africa/Lagos")

def format_datetime(dt):
    """Convert datetime string or object to WAT-formatted string."""
    if not dt:
        return "Unknown"
    if isinstance(dt, datetime):
        return dt.astimezone(WAT).strftime("%A, %d %B %Y at %I:%M %p")
    try:
        parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return parsed.astimezone(WAT).strftime("%A, %d %B %Y at %I:%M %p")
    except Exception:
        return str(dt)

def show():
    st.title("Admin Dashboard")
    st.info("Admin dashboard: manage users, mentorship matches, and sessions.")

    tabs = st.tabs(["📝 Register", "👥 Users", "📩 Requests", "🔁 Matches", "🗓️ Sessions"])

    # 1. Register New User
    with tabs[0]:
        st.subheader("Register New User")
        with st.form("register_user", clear_on_submit=True):
            user_email = st.text_input("User Email", placeholder="e.g. user@example.com")
            role = st.selectbox("Assign Role", ["Select a role", "Mentor", "Mentee"])
            submitted = st.form_submit_button("Create")

        if submitted:
            if not user_email or role == "Select a role":
                st.warning("⚠️ Please fill in both email and role.")
            else:
                register_user(user_email, role)
                st.success(f"✅ User '{user_email}' registered as {role}.")
                time.sleep(1)
                st.rerun()

    # 2. View & Update Users
    with tabs[1]:
        st.subheader("All Users")
        try:
            users = supabase.table("users").select("""
                userid, email, role, must_change_password, profile_completed, created_at, status
            """).neq("status", "Delete").execute().data
        except Exception as e:
            st.error(f"❌ Failed to load users: {e}")
            users = []

        if users:
            df = pd.DataFrame(users)
            df["created_at"] = df["created_at"].apply(format_datetime)
            df = df.rename(columns={
                "userid": "User ID",
                "email": "Email",
                "role": "Role",
                "must_change_password": "Must Change Password",
                "profile_completed": "Profile Completed",
                "created_at": "Created At",
                "status": "Status"
            })

            email_search = st.text_input("🔍 Search by Email").lower()
            status_filter = st.selectbox("📂 Filter by Status", ["All", "Active", "Inactive"])

            filtered_df = df.copy()
            if email_search:
                filtered_df = filtered_df[filtered_df["Email"].str.lower().str.contains(email_search)]
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df["Status"] == status_filter]

            st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

            selected_email = st.selectbox(
                "✏️ Select User to Update",
                ["Select an email..."] + df["Email"].tolist()
            )

            new_status = st.selectbox(
                "🛠️ New Status",
                ["Select status...", "Active", "Inactive", "Delete"]
            )

            confirm_delete_1 = confirm_delete_2 = False
            if new_status == "Delete":
                st.warning("⚠️ Deleting a user is permanent. Please confirm below:")
                confirm_delete_1 = st.checkbox(
                    "I understand that deleting this user is permanent and cannot be undone.",
                    key="confirm_delete_1"
                )
                confirm_delete_2 = st.checkbox(
                    "Yes, I really want to delete this user.",
                    key="confirm_delete_2"
                )

            if st.button("✅ Update Status"):
                if selected_email == "Select an email..." or new_status == "Select status...":
                    st.warning("⚠️ Please select both a valid user and a status.")
                else:
                    user_row = df[df["Email"] == selected_email].iloc[0]
                    user_id = user_row["User ID"]

                    try:
                        if new_status == "Delete":
                            if confirm_delete_1 and confirm_delete_2:
                                supabase.table("users").delete().eq("userid", user_id).execute()
                                st.success(f"✅ Deleted user: {selected_email}")
                                st.rerun()
                            else:
                                st.warning("☑️ You must confirm both checkboxes to proceed with deletion.")
                        else:
                            supabase.table("users").update({"status": new_status}).eq("userid", user_id).execute()
                            st.success(f"✅ Updated {selected_email} to {new_status}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to update user: {e}")
        else:
            st.info("No users found.")

    # 3. Mentorship Requests
    with tabs[2]:
        st.subheader("Mentorship Requests")
        try:
            requests = supabase.table("mentorshiprequest").select("""
                *, mentee:users!mentorshiprequest_menteeid_fkey(email),
                   mentor:users!mentorshiprequest_mentorid_fkey(email)
            """).neq("status", "ACCEPTED").execute().data
        except Exception as e:
            st.error(f"❌ Could not fetch mentorship requests: {e}")
            requests = []

        if requests:
            for req in requests:
                mentee_email = req['mentee']['email']
                mentor_email = req['mentor']['email']
                status = req.get("status", "Unknown")
                st.markdown(f"""
                - 🧑 Mentee: **{mentee_email}**  
                - 🧑‍🏫 Mentor: **{mentor_email}**  
                - 📌 Status: **{status}**
                """)
        else:
            st.info("No mentorship requests found.")

    # 4. Match Mentees to Mentors
    with tabs[3]:
        st.subheader("Match Mentee to Mentor")
        try:
            users = supabase.table("users").select("userid, email, role, status") \
                .neq("status", "Delete").execute().data or []
            mentees = [u for u in users if u["role"] == "Mentee"]
            mentors = [u for u in users if u["role"] == "Mentor"]
        except Exception as e:
            st.error(f"❌ Failed to fetch users: {e}")
            mentees, mentors = [], []

        if not mentees or not mentors:
            st.warning("No available mentees or mentors.")
        else:
            mentee_email = st.selectbox("Select Mentee", [m["email"] for m in mentees])
            mentor_email = st.selectbox("Select Mentor", [m["email"] for m in mentors])

            if st.button("Create Match"):
                if mentee_email == mentor_email:
                    st.warning("Mentee and Mentor cannot be the same.")
                else:
                    mentee_id = next((m["userid"] for m in mentees if m["email"] == mentee_email), None)
                    mentor_id = next((m["userid"] for m in mentors if m["email"] == mentor_email), None)

                    existing = supabase.table("mentorshiprequest") \
                        .select("mentorshiprequestid") \
                        .eq("menteeid", mentee_id).eq("mentorid", mentor_id) \
                        .execute().data

                    if existing:
                        st.warning("This mentorship request already exists.")
                    else:
                        availability = supabase.table("availability") \
                            .select("availabilityid") \
                            .eq("mentorid", mentor_id).execute().data

                        if not availability:
                            st.warning("⚠️ This mentor has no availability slots set.")

                        supabase.table("mentorshiprequest").insert({
                            "menteeid": mentee_id,
                            "mentorid": mentor_id,
                            "status": "ACCEPTED"
                        }).execute()

                        now = datetime.now(tz=WAT)
                        end = now + pd.Timedelta(minutes=30)
                        success, msg = create_session_if_available(supabase, mentor_id, mentee_id, now, end)

                        if success:
                            st.success("✅ Match created and session booked!")
                        else:
                            st.warning(msg)
                        st.rerun()

    # 5. Sessions
    with tabs[4]:
        st.subheader("All Sessions")
        try:
            sessions = supabase.table("session").select("""
                *, mentor:users!session_mentorid_fkey(email),
                   mentee:users!session_menteeid_fkey(email)
            """).execute().data
        except Exception as e:
            st.error(f"❌ Could not fetch sessions: {e}")
            sessions = []

        if sessions:
            for s in sessions:
                st.markdown(f"""
                - 🧑‍🏫 Mentor: **{s['mentor']['email']}**  
                - 🧑 Mentee: **{s['mentee']['email']}**  
                - 📅 Date: {format_datetime_safe(s.get('date'))}  
                - ⭐ Rating: {s.get('rating', 'Not rated')}  
                - 💬 Feedback: {s.get('feedback', 'No feedback')}  
                - 🔗 [Join Meet]({s.get('meet_link', '#')})
                """)
        else:
            st.info("No sessions found.")
