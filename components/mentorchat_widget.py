import streamlit as st
from utils.mentorchat import mentorchat

def mentorchat_widget():
    # Only show if toggle is ON
    if not st.session_state.get("show_mentor_chat", False):
        return

    st.markdown("### 🤖 MentorChat", help="Ask any question about using MentorLink")
    with st.expander("💬 Chat with MentorChat", expanded=True):
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display chat history
        for entry in st.session_state.chat_history:
            if entry["sender"] == "user":
                st.markdown(f"🧑‍💻 **You:** {entry['message']}")
            else:
                st.markdown(f"🤖 **MentorChat:** {entry['message']}")

        # Chat input
        def handle_chat():
            user_input = st.session_state.get("mentor_input", "").strip()
            role = st.session_state.get("role", "Guest")

            if user_input:
                st.session_state.chat_history.append({"sender": "user", "message": user_input})
                response = mentorchat(user_input, user_role=role)
                st.session_state.chat_history.append({"sender": "bot", "message": response})
                st.session_state["mentor_input"] = ""

        st.text_input("Type a message", key="mentor_input", on_change=handle_chat)
