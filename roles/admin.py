import sys
import os
import time
from datetime import datetime
import streamlit as st
import pandas as pd

# Adjust path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import supabase
from auth.auth_handler import register_user
from utils.session_creator import create_session_with_meet_and_email


# Safe datetime formatter
def format_datetime(dt):
    if not dt:
        return "Unknown"
    if isinstance(dt, datetime):
        return dt.strftime("%A, %d %B %Y at %I:%M %p")
    try:
        parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return parsed.strftime("%A, %d %B %Y at %I:%M %p")
    except Exception:
        return str(dt)

# Placeholder for session creation (ensure your actual logic handles timing properly)
def create_session(mentorid, menteeid, request_id):
    now = datetime.utcnow()
    end = now + pd.Timedelta(minutes=30)
    success, msg = create_session_if_available(supabase, mentorid, menteeid, now, end)
    return success, msg

def show():
    st.title("Admin Dashboard")
    st.info("Admin dashboard features: manage users, matches, and sessions.")

    tabs = st.tabs(["📝 Register", "👥 Users", "🔁 Matches", "🗖 Sessions"])

    # --------------------- 📝 Register Tab --------------------- #
    with tabs[0]:
        st.subheader("Register New User")
        with st.form("register_user", clear_on_submit=True):
            user_email = st.text_input("User Email", placeholder="e.g. user@example.com")
            roles = ["Select a role", "Mentor", "Mentee"]
            role = st.selectbox("Assign Role", roles)
            submitted = st.form_submit_button("Create")

        if submitted:
            if not user_email or role == "Select a role":
                st.warning("⚠️ Please fill in both email and role.")
            else:
                register_user(user_email, role)
                st.success(f"✅ User '{user_email}' registered as {role}.")
                time.sleep(2)
                st.rerun()

    # --------------------- 👥 Users Tab --------------------- #
    with tabs[1]:
        st.subheader("All Users")
        try:
            users = supabase.table("users").select("""
                userid, email, role, must_change_password, profile_completed, created_at, status
            """).neq("status", "Delete").execute().data
        except Exception as e:
            st.error(f"Failed to load users: {e}")
            users = []

        if users:
            email_search = st.text_input("Search by Email").lower()
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])

            st.markdown("#### User Table")
            for i, user in enumerate(users, 1):
                email = user.get("email", "").lower()
                status = user.get("status", "Active")
                if email_search and email_search not in email:
                    continue
                if status_filter != "All" and status != status_filter:
                    continue

                is_admin = email == "admin@theincubatorhub.com"
                user_id = user.get("userid")

                cols = st.columns([0.3, 2.2, 1.5, 1.2, 1.2, 2.5, 1.5, 1])
                cols[0].markdown(f"{i}")
                cols[1].markdown(user["email"])
                cols[2].markdown(user["role"])
                cols[3].markdown("N/A" if is_admin else str(user["must_change_password"]))
                cols[4].markdown("N/A" if is_admin else str(user["profile_completed"]))
                cols[5].markdown(format_datetime(user.get("created_at")) if user.get("created_at") else "-")

                if is_admin:
                    cols[6].markdown("N/A")
                    cols[7].markdown("🚫")
                    continue

                new_status = cols[6].selectbox(
                    "", ["Active", "Inactive", "Delete"],
                    index=["Active", "Inactive", "Delete"].index(user["status"]),
                    key=f"status_{user_id}"
                )
                confirm_key = f"confirm_delete_{user_id}"
                confirm_delete = cols[6].checkbox("⚠️ Confirm", key=confirm_key) if new_status == "Delete" else False

                if cols[7].button("Update", key=f"update_{user_id}"):
                    try:
                        if new_status == "Delete":
                            if confirm_delete:
                                supabase.table("users").delete().eq("userid", user_id).execute()
                                st.success(f"✅ Deleted user: {user['email']}")
                            else:
                                st.warning("☑️ Please confirm deletion.")
                        else:
                            supabase.table("users").update({"status": new_status}).eq("userid", user_id).execute()
                            st.success(f"Updated {user['email']} to {new_status}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to update user: {e}")
        else:
            st.info("No users found.")

    # --------------------- 🔁 Requests Tab --------------------- #
    with tabs[2]:
        st.subheader("Mentorship M")

        try:
            requests = supabase.table("mentorshiprequest").select("""
                *, mentee:users!mentorshiprequest_menteeid_fkey(email),
                   mentor:users!mentorshiprequest_mentorid_fkey(email)
            """).execute().data
        except Exception as e:
            st.error(f"Could not fetch mentorship requests: {e}")
            requests = []

        if requests:
            for req in requests:
                st.markdown(f"""
                - Mentee: **{req['mentee']['email']}**
                - Mentor: **{req['mentor']['email']}**
                - Status: **{req.get('status', 'Unknown')}**
                """)

        st.markdown("---")
        with st.expander("🔗 Match Mentee to Mentor"):
            users = supabase.table("users").select("userid, email, role, status") \
                .neq("status", "Delete").execute().data
            mentees = [u for u in users if u["role"] == "Mentee"]
            mentors = [u for u in users if u["role"] == "Mentor"]

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
                            result = supabase.table("mentorshiprequest").insert({
                                "menteeid": mentee_id,
                                "mentorid": mentor_id,
                                "status": "ACCEPTED"
                            }).execute()
                            request_id = result.data[0]["mentorshiprequestid"]
                            success, msg = create_session(mentor_id, mentee_id, request_id)
                            st.success("✅ Match created and session booked!" if success else msg)
                            st.rerun()

    # --------------------- 🗖 Sessions Tab --------------------- #
    with tabs[3]:
        st.subheader("All Sessions")
        try:
            sessions = supabase.table("session").select("""
                *, mentor:users!session_mentorid_fkey(email),
                   mentee:users!session_menteeid_fkey(email)
            """).execute().data
        except Exception as e:
            st.error(f"Could not fetch sessions: {e}")
            sessions = []

        if sessions:
            for s in sessions:
                st.markdown(f"""
                - Mentor: **{s['mentor']['email']}**
                - Mentee: **{s['mentee']['email']}**
                - Date: {format_datetime(s.get('date'))}
                - Rating: {s.get('rating', 'Not rated')}
                - Link: [Join Meet]({s.get('meet_link', '#')})
                """)
        else:
            st.info("No sessions found.")
