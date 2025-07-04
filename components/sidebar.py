import streamlit as st
from auth.auth_handler import logout
from database import supabase  # Ensure supabase client is properly imported

def sidebar():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    with st.sidebar:
        # ✅ Greeting Section
        if st.session_state.get("logged_in") and "user" in st.session_state:
            user = st.session_state["user"]
            user_id = user.get("userid")
            user_email = user.get("email", "")

            # Default fallback name (before fetching profile name)
            fallback_name = user_email.split("@")[0].capitalize()
            full_name = fallback_name

            # ✅ Use profile.name if not admin
            if user_email.lower() != "admin@theincubatorhub.com":
                try:
                    profile_result = supabase.table("profile").select("name").eq("userid", user_id).single().execute()
                    profile = profile_result.data
                    if profile and profile.get("name"):
                        full_name = profile["name"]
                 except Exception as e:
                     st.warning("")
                    # Optionally, log error e

            st.success(f"👋 Welcome, {full_name}!")

            # ✅ Logout Button
            if st.button("🔓 Logout", key="logout_sidebar"):
                logout()
                st.session_state["do_rerun"] = True
                st.experimental_rerun()

        # ✅ Toggle MentorChat
        chat_visible = st.checkbox("💬 Toggle MentorChat", key="toggle_mentor_chat")
        st.session_state["show_mentor_chat"] = chat_visible

        st.markdown("---")

        # ✅ About Section
        st.title("About MentorLink")
        st.info(
            "**MentorLink**\n\n"
            "_...unlocking success through purposeful mentorship connections._"
        )

        # ✅ Contact Info
        st.markdown("**📞 Contact Us:**")
        st.markdown("- [💬 Chat with the Support Team](https://wa.me/2348062529172)")

        st.markdown("---")

        # ✅ Developer Info
        st.markdown("# 👨‍💻 App Developer")
        st.markdown(
            """
**Ezekiel BALOGUN**  
* _Full-Stack Developer_  
* _Data Scientist / Analyst_  
* _AI / Machine Learning Engineer_  
* _Automation / BI Expert_

📧 [ezekiel4true@yahoo.com](mailto:ezekiel4true@yahoo.com)  
🔗 [LinkedIn](https://www.linkedin.com/in/ezekiel-balogun-39a14438)  
📞 +2348062529172
            """
        )
