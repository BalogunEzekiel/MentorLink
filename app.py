import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from roles.utils import format_datetime
from auth import login, logout, register_user, get_user_role, change_password, profile_form
from roles import admin, mentor, mentee

st.set_page_config(page_title="MentorLink", layout="wide")

if not st.session_state.get("authenticated", False):
    login()
else:
    role = st.session_state.get("role")
    user = st.session_state.get("user", {})

    if role != "Admin":
        if user.get("must_change_password", False):
            change_password()
        elif not user.get("profile_completed", False):
            profile_form()
        else:
            st.sidebar.button("Logout", on_click=logout)
            if role == "Mentor":
                mentor.show()
            elif role == "Mentee":
                mentee.show()
    else:
        st.sidebar.button("Logout", on_click=logout)
        admin.show()

#import sys
#st.write("Python Path:", sys.path)
