# Handles login, register, session state, and Supabase auth integration
import streamlit as st
from supabase import create_client, Client
import bcrypt
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

DEFAULT_PASSWORD = "default@1234"  # 🔐 Admin's assigned default

# One-time setup: Create Admin if not exists
def setup_admin_account():
    admin_email = "admin@theincubatorhub.com"
    admin_password = "Admin@123"
    admin_role = "Admin"

    result = supabase.table("users").select("*").eq("email", admin_email).execute()
    print("Admin lookup result:", result.data)
    if result.data:
        return  # Admin already exists

    hashed_pw = bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    admin_id = str(uuid.uuid4())

    try:
        supabase.table("users").insert({
            # Optional: You can omit this if Supabase uses default UUID
            "userid": str(uuid.uuid4()),
            "email": admin_email,
            "password": hashed_pw,
            "role": admin_role,
            "must_change_password": False,
            "profile_completed": True
        }).execute()
        print("✅ Admin account created.")
    except Exception as e:
        print("🔥 Failed to insert admin account:")
        print(e)

setup_admin_account()

def login():
    st.title("Login")

    email = st.text_input("Email").strip().lower()
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
            return

        try:
            result = supabase.table("users").select("*").eq("email", email).execute()
            users = result.data
        except Exception as e:
            st.error("An error occurred while connecting to the database.")
            st.exception(e)
            return

        if not users:
            st.error("You must be registered by the Admin before log-in.")
            return

        user = users[0]
        stored_hashed = user.get("password")

        if bcrypt.checkpw(password.encode("utf-8"), stored_hashed.encode("utf-8")):
            st.session_state.authenticated = True
            st.session_state.user = user
            st.session_state.role = user.get("role")

            role = user.get("role", "")
            if role == "Admin":
                # 🔐 Skip password change and profile setup
                st.success("Welcome Admin! Redirecting to dashboard...")
            else:
                # 🔁 Enforce setup for mentors/mentees
                if user.get("must_change_password"):
                    st.session_state.force_change_password = True
                elif not user.get("profile_completed"):
                    st.session_state.force_profile_update = True

            st.rerun()
        else:
            st.error("Invalid password.")
        
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state["do_rerun"] = True  # ✅ Set a rerun flag

def get_user_role():
    return st.session_state.get("role", None)

def register_user(email, role):
    default_password = "changeme123"
    hashed_pw = bcrypt.hashpw(default_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    result = supabase.table("users").select("*").eq("email", email).execute()
    if result.data:
        return f"User with email {email} already exists."

    supabase.table("users").insert({
        "email": email,
        "password": hashed_pw,
        "role": role,
        "must_change_password": True,
        "profile_completed": False
    }).execute()

    from mailer import send_welcome_email
    send_welcome_email(email, default_password)

    return f"User {email} registered and notified via email."

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

        userid = st.session_state.user.get("userid")

        if not userid:
            st.error("User ID not found in session.")
            return

        try:
            response = supabase.table("profile").insert({
                "userid": userid,
                "name": name,
                "bio": bio,
                "skills": skills,
                "goals": goals
            }).execute()
            st.success("Profile submitted.")
        except Exception as e:
            st.error("Error submitting profile.")
            st.exception(e)

        # ✅ Update the correct column in the users table
        supabase.table("users").update({"profile_completed": True}) \
            .eq("userid", userid).execute()

        del st.session_state["force_profile_update"]
        st.success("Profile submitted.")
        st.rerun()

def change_password():
    st.title("🔐 Change Password")

    new_password = st.text_input("Enter new password", type="password")
    confirm_password = st.text_input("Confirm new password", type="password")

    if st.button("Update Password"):
        if not new_password or not confirm_password:
            st.warning("Please fill in both fields.")
            return
        if new_password != confirm_password:
            st.error("Passwords do not match.")
            return

        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        userid = st.session_state.user.get("userid")

        supabase.table("users").update({
            "password": hashed_pw,
            "must_change_password": False
        }).eq("userid", userid).execute()

        del st.session_state["force_change_password"]
        st.success("Password updated successfully.")
        st.rerun()
