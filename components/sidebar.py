import streamlit as st
from auth.auth_handler import logout
from database import supabase  # make sure this is imported

def sidebar():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    with st.sidebar:
        # ✅ Greeting Section
        if st.session_state.get("logged_in") and "user" in st.session_state:
            user = st.session_state["user"]
            user_id = user.get("userid")

            # Default fallback name
            fallback_name = user.get("email", "User").split("@")[0].capitalize()
            full_name = fallback_name

            # ✅ Try to fetch profile.name from DB
            try:
                profile = supabase.table("profile").select("name") \
                    .eq("userid", user_id).single().execute().data
                if profile and profile.get("name"):
                    full_name = profile["name"]
            except Exception as e:
                st.warning("Could not load profile name.")

            st.success(f"👋 Welcome, {full_name}!")
#==========================================================================================
            # ✅ Logout Button
            if st.button("🔓 Logout", key="logout_sidebar"):
                logout()
                st.session_state["do_rerun"] = True

        # ✅ Toggle MentorChat
        chat_visible = st.toggle("💬 Toggle MentorChat", key="toggle_mentor_chat")
        st.session_state["show_mentor_chat"] = chat_visible

        st.markdown("---")

        # ✅ About Section
        st.sidebar.title("About MentorLink")
        st.info("**MentorLink**\n\n"
                "_...unlocking success through purposeful mentorship connections._")

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
