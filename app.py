import streamlit as st
import sys
import os

# Ensure correct path resolution for local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import utility functions and role views
from roles.utils import format_datetime
from auth import login, logout, register_user, get_user_role, change_password, profile_form
from roles import admin, mentor, mentee

# Set app configuration
st.set_page_config(page_title="MentorLink", layout="wide")

# ROUTER: Handle authentication and role-based rendering
if not st.session_state.get("authenticated", False):
    login()  # Show login screen
else:
    role = st.session_state.get("role")
    user = st.session_state.get("user", {})

    # Non-admins go through onboarding steps
if role != "Admin":
    if st.session_state.user.get("must_change_password", False):
        change_password()
    elif not st.session_state.user.get("profile_completed", False):
        profile_form()
    else:
        st.sidebar.button("Logout", on_click=logout)
        if role == "Mentor":
            mentor.show()
        elif role == "Mentee":
            mentee.show()
    else:
        # Admin bypasses onboarding
        st.sidebar.button("Logout", on_click=logout)
        admin.show()
