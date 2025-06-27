import streamlit as st
from utils.mentorchat import mentorchat

def handle_input():
    user_input = st.session_state.get("mentor_input", "").strip()
    role = st.session_state.get("role", "Guest")

    if user_input:
        # Store user input
        st.session_state.chat_history.append({"sender": "user", "message": user_input})

        # Generate bot response
        response = mentorchat(user_input, user_role=role)

        # Store bot response
        st.session_state.chat_history.append({"sender": "bot", "message": response})

        # Clear the input field
        st.session_state["mentor_input"] = ""

def show_mentor_chat():
    st.subheader("### 💬 MentorChat - Your Mentorship Assistant")

    # Initialize chat history if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display existing chat history
    for entry in st.session_state.chat_history:
        if entry["sender"] == "user":
            st.markdown(f"🧑‍💻 **You:** {entry['message']}")
        else:
            st.markdown(f"🤖 **MentorChat:** {entry['message']}")

    # Input box with callback handler
    st.text_input("Type your message and press Enter", key="mentor_input", on_change=handle_input)
