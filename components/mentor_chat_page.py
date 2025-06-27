import streamlit as st
from utils.mentorchat import mentorchat

def show_mentor_chat():
    st.title("💬 MentorChat - Your Personal Assistant")

    role = st.session_state.get("role", "Mentee")  # Default to Mentee if not logged in

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Type your message here:")

    if user_input:
        response = mentorchat(user_input, role)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("MentorChat", response))
        st.rerun()

    # Display chat history
    for sender, msg in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"**🧑‍💬 {sender}:** {msg}")
        else:
            st.markdown(f"**🤖 {sender}:** {msg}")

    # Optional: Clear Chat button
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()
