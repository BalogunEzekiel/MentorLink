import streamlit as st
import time
from utils.mentorchat import mentorchat  # Ensure this is the updated chatbot logic

def show_mentor_chat():
    st.markdown("## 🤖 MentorChat Assistant")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Get user input
    user_input = st.chat_input("Ask MentorChat anything...")

    # Get user role
    role = st.session_state.get("role", "Public")

    # If input submitted
    if user_input:
        st.session_state.chat_history.append(("user", user_input))

        # Get bot response
        bot_response = mentorchat(user_input, user_role=role)
        st.session_state.chat_history.append(("bot", bot_response))

    # Display chat history
    for sender, message in st.session_state.chat_history:
        if sender == "user":
            with st.chat_message("user"):
                st.write(message)
        else:
            with st.chat_message("assistant"):
                simulate_typing(message)

# 🔄 Typing Simulation
def simulate_typing(response: str, delay: float = 0.02):
    """Displays the bot response with a typing simulation."""
    displayed = ""
    message_placeholder = st.empty()

    for char in response:
        displayed += char
        message_placeholder.markdown(displayed + "▌")  # Simulated cursor
        time.sleep(delay)

    message_placeholder.markdown(displayed)  # Final output
