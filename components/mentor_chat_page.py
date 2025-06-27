import streamlit as st
from utils.mentorchat import mentorchat

def show_mentor_chat():
    st.title("💬 MentorChat - Your Mentorship Assistant")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Role from session
    role = st.session_state.get("role", "Guest")

    # Display previous chat
    for entry in st.session_state.chat_history:
        if entry["sender"] == "user":
            st.markdown(f"🧑‍💻 **You:** {entry['message']}")
        else:
            st.markdown(f"🤖 **MentorChat:** {entry['message']}")

    # User input
    user_input = st.text_input("Type your message and press Enter", key="mentor_input")

    if user_input:
        # Append user message
        st.session_state.chat_history.append({"sender": "user", "message": user_input})

        # Get chatbot response
        response = mentorchat(user_input, user_role=role)

        # Append bot response
        st.session_state.chat_history.append({"sender": "bot", "message": response})

        # Clear input for next message
        st.session_state["mentor_input"] = ""
        st.rerun()  # Safe here, only triggers one clean rerun
