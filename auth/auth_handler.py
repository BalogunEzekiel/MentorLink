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

    email = st.text_input("Email").strip().lower()
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
            return

        # 🔍 Fetch user by email (case-insensitive)
        result = supabase.table("users").select("*").ilike("email", email).execute()
        users = result.data

        if not users:
            st.error("You must be registered by the Admin before logging in.")
            return

        user = users[0]

        # 🚫 Check for inactive/deleted status
        status = user.get("status", "Active")
        if status in ["Inactive", "Delete"]:
            st.error(f"Your account is {status.lower()}. Contact admin.")
            return

        # 🔐 Check password
        stored_hashed = user.get("password")
        if bcrypt.checkpw(password.encode("utf-8"), stored_hashed.encode("utf-8")):
            # ✅ Store session info
            st.session_state.authenticated = True
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.role = user.get("role")

            # 🧑‍💼 Admin role
            if user["email"].lower() == "admin@theincubatorhub.com":
                st.session_state["user_display_name"] = "Admin"
            else:
                # 🧾 Get profile name if exists
                try:
                    result = supabase.table("profile").select("name").eq("userid", user["userid"]).limit(1).execute()
                    profile_data = result.data
                    if profile_data:
                        st.session_state["user_display_name"] = profile_data[0]["name"]
                    else:
                        st.session_state["user_display_name"] = "User"
                except Exception:
                    st.session_state["user_display_name"] = "User"

            # 🎯 Force flows
            if user.get("role") == "Admin":
                st.success("Welcome Admin! Redirecting...")
            elif user.get("must_change_password"):
                st.session_state.force_change_password = True
            elif not user.get("profile_completed"):
                st.session_state.force_profile_update = True

            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid password.")

def logout():
    # 🔐 Clear all session keys
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state["do_rerun"] = True

def register_user(email, role):
    # 📌 Default password for new users
    hashed_pw = bcrypt.hashpw("changeme123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # 🧾 Check for duplicate
    result = supabase.table("users").select("*").eq("email", email).execute()
    if result.data:
        return f"User with email {email} already exists."

    # ✅ Insert new user
    supabase.table("users").insert({
        "email": email,
        "password": hashed_pw,
        "role": role,
        "must_change_password": True,
        "profile_completed": False,
        "status": "Active"
    }).execute()
