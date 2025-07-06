import streamlit as st
import bcrypt
import time
from database import supabase
from datetime import datetime
import pytz

# West Africa Timezone (UTC+1)
WAT = pytz.timezone("Africa/Lagos")

def login():
    st.title("Login")

    email = st.text_input("Email", placeholder="Enter your email address").strip().lower()
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
            return

        try:
            # Fetch user (case-insensitive)
            result = supabase.table("users").select("*").ilike("email", email).execute()
            users = result.data
        except Exception as e:
            st.error(f"Error fetching user: {e}")
            return

        if not users:
            st.error("You must be registered by the Admin before logging in.")
            return

        user = users[0]

        # Check status
        status = user.get("status", "Active")
        if status in ["Inactive", "Delete"]:
            st.error(f"Your account is {status.lower()}. Contact admin.")
            return

        # Validate password
        stored_hashed = user.get("password")
        if not stored_hashed or not bcrypt.checkpw(password.encode("utf-8"), stored_hashed.encode("utf-8")):
            st.error("Invalid password.")
            return

        # ✅ Login Success - Set session state
        st.session_state.authenticated = True
        st.session_state.logged_in = True
        st.session_state.user = user
        st.session_state.role = user.get("role")

        # 🧑 Set display name
        user_email = user["email"].lower()
        if user_email == "admin01@theincubatorhub.com":
            st.session_state["user_display_name"] = "Admin I"
        elif user_email == "admin02@theincubatorhub.com":
            st.session_state["user_display_name"] = "Admin II"
        else:
            try:
                profile_result = supabase.table("profile").select("name").eq("userid", user["userid"]).limit(1).execute()
                profile_data = profile_result.data
                st.session_state["user_display_name"] = profile_data[0]["name"] if profile_data else "User"
            except Exception:
                st.session_state["user_display_name"] = "User"

        # 🕒 Log login time
        try:
            supabase.table("userlogins").insert({
                "userid": user["userid"],
                "login_time": datetime.now(WAT).isoformat(),
                "timezone": "WAT"
            }).execute()
        except:
            pass  # Silent fail

        # 🔀 Redirects
        if user.get("role") == "Admin":
            pass  # Optional: add admin redirect logic
        elif user.get("must_change_password"):
            st.session_state.force_change_password = True
        elif not user.get("profile_completed"):
            st.session_state.force_profile_update = True

        st.rerun()


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def register_user(email, role):
    hashed_pw = bcrypt.hashpw("changeme123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Prevent duplicates
    result = supabase.table("users").select("*").eq("email", email).execute()
    if result.data:
        return f"User with email {email} already exists."

    # Register new user
    supabase.table("users").insert({
        "email": email,
        "password": hashed_pw,
        "role": role,
        "must_change_password": True,
        "profile_completed": False,
        "status": "Active",
        "created_at": datetime.now(WAT).isoformat()
    }).execute()
