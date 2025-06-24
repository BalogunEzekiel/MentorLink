# Handles login, register, session state, and Supabase auth integration
import streamlit as st
from supabase import create_client, Client
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
            return

        result = supabase.table("users").select("*").eq("email", email).execute()
        if result.data:
            user = result.data[0]
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.role = user["role"]

                if user["role"] != "Admin":
                    if user.get("must_change_password", False):
                        st.session_state.force_change_password = True
                    else:
                        # Check if profile exists
                        profile = supabase.table("profile").select("*").eq("userid", user["userid"]).execute()
                        if not profile.data:
                            st.session_state.force_profile_update = True

                st.rerun()
            else:
                st.error("Incorrect password.")
        else:
            st.error("User not found.")

# One-time setup: Create Admin if not exists
def setup_admin_account():
    admin_email = "admin@theincubatorhub.com"
    admin_password = "Admin@123"  # 🔒 Replace or hash externally for security
    admin_role = "Admin"

    # Check if admin already exists
    result = supabase.table("users").select("*").eq("email", admin_email).execute()
    if result.data:
        return  # Admin already exists, no action needed

    # Create admin account
    import bcrypt
    hashed_pw = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()

    supabase.table("users").insert({
        "email": admin_email,
        "password": hashed_pw,
        "role": admin_role
    }).execute()
    print("✅ Admin account created.")

setup_admin_account()

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state["do_rerun"] = True  # ✅ Set a rerun flag

def get_user_role():
    return st.session_state.get("role", None)

def register_user(email, role):
    existing = supabase.table("users").select("*").eq("email", email).execute()
    if existing.data:
        return "User already exists."

    default_password = "default-1234"
    hashed_pw = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()

    user_data = {
        "email": email,
        "password": hashed_pw,
        "role": role,
        "must_change_password": True
    }

    try:
        supabase.table("users").insert(user_data).execute()
        return f"{role} user '{email}' created successfully with default password."
    except Exception:
        return "Failed to create user."

def change_password():
    st.title("Change Your Password")

    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Update Password"):
        if new_password != confirm_password:
            st.warning("Passwords do not match.")
            return
        if len(new_password) < 6:
            st.warning("Password must be at least 6 characters.")
            return

        hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        supabase.table("users").update({
            "password": hashed_pw,
            "must_change_password": False
        }).eq("email", st.session_state.user["email"]).execute()

        st.success("Password updated. Please log in again.")
        st.session_state.clear()
        st.rerun()

def profile_form():
    st.title("🧑‍💼 Complete Your Profile")

    name = st.text_input("Full Name")
    bio = st.text_area("Bio", max_chars=500)
    skills = st.text_input("Skills (comma-separated)")
    goals = st.text_area("Your Goals")

    if st.button("Submit Profile"):
        if not name or not bio or not skills or not goals:
            st.warning("All fields are required.")
            return

        supabase.table("profile").insert({
            "userid": st.session_state.user["userid"],
            "name": name,
            "bio": bio,
            "skills": skills,
            "goals": goals
        }).execute()

        # Optional: update profile_completed flag in users table
        supabase.table("users").update({"profile_completed": True}) \
            .eq("id", st.session_state.user["userid"]).execute()

        del st.session_state["force_profile_update"]
        st.success("Profile submitted.")
        st.rerun()
