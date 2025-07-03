import streamlit as st
import time
import bcrypt
from database import supabase
from datetime import datetime
import pytz

# West Africa Timezone (UTC+1)
WAT = pytz.timezone("Africa/Lagos")

def profile_form():
    st.title("🧑‍💼 Complete Your Profile")

    name = st.text_input("Full Name")
    bio = st.text_area("Bio", max_chars=500)
    skills = st.text_input("Skills (comma-separated)")
    goals = st.text_area("Your Goals")

    if st.button("Submit Profile"):
        if not all([name, bio, skills, goals]):
            st.warning("All fields are required.")
            return

        userid = st.session_state.user.get("userid")
        now_wat = datetime.now(WAT).isoformat()

        existing = supabase.table("profile").select("*").eq("userid", userid).execute()

        if existing.data:
            supabase.table("profile").update({
                "name": name,
                "bio": bio,
                "skills": skills,
                "goals": goals,
                "updated_at": now_wat
            }).eq("userid", userid).execute()
        else:
            supabase.table("profile").insert({
                "userid": userid,
                "name": name,
                "bio": bio,
                "skills": skills,
                "goals": goals,
                "created_at": now_wat,
                "updated_at": now_wat
            }).execute()

        supabase.table("users").update({
            "profile_completed": True,
            "profile_updated_at": now_wat
        }).eq("userid", userid).execute()

        st.session_state.user["profile_completed"] = True
        st.session_state.pop("force_profile_update", None)

        # Store name for greeting
        profile = supabase.table("profile").select("name").eq("userid", userid).single().execute().data
        if profile:
            st.session_state["user_display_name"] = profile.get("name")

        st.success("✅ Profile completed!")
        time.sleep(1)
        st.rerun()


def change_password():
    st.title("🔐 Change Password")

    new_pw = st.text_input("Enter new password", type="password")
    confirm_pw = st.text_input("Confirm new password", type="password")

    if st.button("Update Password"):
        if not new_pw or not confirm_pw:
            st.warning("Please fill in both fields.")
            return
        if new_pw != confirm_pw:
            st.error("Passwords do not match.")
            return

        userid = st.session_state.user.get("userid")
        hashed_pw = bcrypt.hashpw(new_pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        now_wat = datetime.now(WAT).isoformat()

        supabase.table("users").update({
            "password": hashed_pw,
            "must_change_password": False,
            "password_updated_at": now_wat
        }).eq("userid", userid).execute()

        st.session_state.user["must_change_password"] = False
        st.session_state.force_profile_update = True
        st.success("✅ Password updated!")
        time.sleep(1)
        st.rerun()
