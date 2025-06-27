import streamlit as st
from utils.mentorchat import mentorchat

def show_mentorchat_widget():
    # Only show widget if toggled
    if not st.session_state.get("show_mentor_chat", False):
        return

    # Initialize chat state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "mentor_input" not in st.session_state:
        st.session_state.mentor_input = ""

    # Floating style container using columns
    with st.sidebar.expander("💬 Chat with MentorChat", expanded=True):
        st.markdown("**Ask any question about using MentorLink.**")

        # Scrollable chat history
        chat_container = st.container()
        with chat_container:
            for entry in st.session_state.chat_history:
                sender = "🧑‍💻 **You:**" if entry["sender"] == "user" else "🤖 **MentorChat:**"
                st.markdown(f"{sender} {entry['message']}")

        # Input field and send
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input(
                "Type a message...",
                value=st.session_state.mentor_input,
                label_visibility="collapsed",
                key="mentor_input_field"
            )
        with col2:
            if st.button("Send", key="send_chat_button"):
                cleaned_input = user_input.strip()
                if cleaned_input:
                    # Save user message
                    st.session_state.chat_history.append({"sender": "user", "message": cleaned_input})
                    # Get bot response
                    role = st.session_state.get("role", "Guest")
                    response = mentorchat(cleaned_input, user_role=role)
                    st.session_state.chat_history.append({"sender": "bot", "message": response})
                    # Clear input
                    st.session_state.mentor_input = ""
                    st.rerun()  # To reflect new messages

        if st.button("❌ Close Chat", key="close_chat"):
            st.session_state["show_mentor_chat"] = False
            st.session_state["mentor_input"] = ""
