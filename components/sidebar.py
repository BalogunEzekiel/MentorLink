import streamlit as st
from auth.auth_handler import logout
from database import supabase

def sidebar():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    with st.sidebar:

        # ✅ Authenticated User
        if st.session_state.get("logged_in") and "user" in st.session_state:
            user = st.session_state["user"]
            user_email = user.get("email", "").lower()
            user_id = user.get("userid")

            # Default name from email prefix
            fallback_name = user_email.split("@")[0].capitalize()
            full_name = fallback_name

            # ✅ Show full name from profile if not admin
            admin_emails = {"admin01@theincubatorhub.com", "admin02@theincubatorhub.com"}
            if user_email not in admin_emails:
                try:
                    profile_result = supabase.table("profile").select("name").eq("userid", user_id).single().execute()
                    profile = profile_result.data
                    if profile and profile.get("name"):
                        full_name = profile["name"]
                except Exception:
                    pass  # Optionally log this

            st.success(f"👋 Welcome, {full_name}!")

            if st.button("🔓 Logout", key="logout_sidebar"):
                logout()
                st.experimental_rerun()

        st.markdown("### 💬 Chat")
        st.session_state["show_mentor_chat"] = st.checkbox("Toggle MentorChat", key="toggle_mentor_chat")

        st.markdown("---")

        # ✅ About Section
        st.markdown("## 📘 About MentorLink")
        st.info("_...unlocking success through purposeful mentorship connections._")

        st.markdown("### 📞 Contact Us")
        st.markdown("[💬 Chat with Support Team](https://wa.me/2348062529172)")

        st.markdown("---")

        # ✅ Developer Info
        st.markdown("## 👨‍💻 App Developer")
        st.markdown(
            """
**Ezekiel BALOGUN**  
_Full-Stack Developer_  
_Data Scientist / Analyst_  
_AI / Machine Learning Engineer_  
_Automation / BI Expert_  

📧 [ezekiel4true@yahoo.com](mailto:ezekiel4true@yahoo.com)  
🔗 [LinkedIn](https://www.linkedin.com/in/ezekiel-balogun-39a14438)  
📞 +2348062529172
            """
        )
