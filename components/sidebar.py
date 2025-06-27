import streamlit as st
from auth.auth_handler import logout

def sidebar():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    with st.sidebar:
        # ✅ Greeting
        if st.session_state.get("logged_in") and "user" in st.session_state:
            user = st.session_state["user"]
            full_name = user.get("fullname") or user.get("email", "User").split("@")[0].capitalize()
            st.success(f"👋 Welcome, {full_name}!")

            # ✅ Logout button
            if st.button("Logout", key="logout_sidebar"):
                logout()
                st.session_state["do_rerun"] = True

        # ✅ 🔹 Add MentorChat Button
        if st.button("💬 Chat with MentorChat"):
            st.session_state["show_mentor_chat"] = True  # trigger chatbot page

        st.markdown("---")

        st.sidebar.title("About MentorLink")
        st.info("**MentorLink**\n\n"
                "_...unlocking success through purposeful mentorship connections._")

        st.markdown("**📞 Contact Us:**")
        st.markdown("- [💬 Chat with the Support Team](https://wa.me/2348062529172)")
        st.markdown("---")
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
