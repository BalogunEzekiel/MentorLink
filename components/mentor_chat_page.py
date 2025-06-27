import streamlit as st

import time

from utils.mentorchat import mentorchat  # Ensure this is the updated chatbot logic



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

        # Save user message

        st.session_state.chat_history.append(("user", user_input))



        # Add placeholder for bot response (will be replaced during typing)

        st.session_state.chat_history.append(("bot", "...typing..."))



        # Rerun to show user message first, then simulate bot response

        st.session_state["pending_response"] = {

            "input": user_input,

            "role": role

        }

        st.rerun()



    # Check if bot response needs to be generated

    if "pending_response" in st.session_state:

        user_input = st.session_state["pending_response"]["input"]

        role = st.session_state["pending_response"]["role"]



        # Remove the "...typing..." placeholder

        if st.session_state.chat_history and st.session_state.chat_history[-1][1] == "...typing...":

            st.session_state.chat_history.pop()



        # Generate response

        bot_response = mentorchat(user_input, user_role=role)

        st.session_state.chat_history.append(("bot", bot_response))



        # Clean up

        del st.session_state["pending_response"]



        # Rerun again to display animated typing

        st.rerun()



    # Display chat history

    for sender, message in st.session_state.chat_history:

        if sender == "user":

            with st.chat_message("user"):

                st.write(message)

        else:

            with st.chat_message("assistant"):

                if message == st.session_state.chat_history[-1][1]:

                    simulate_typing(message)  # Typing simulation only for latest

                else:

                    st.write(message)



# 🔄 Typing Simulation

def simulate_typing(response: str, delay: float = 0.02):

    displayed = ""

    message_placeholder = st.empty()



    for char in response:

        displayed += char

        message_placeholder.markdown(displayed + "▌")

        time.sleep(delay)



    message_placeholder.markdown(displayed)  # Final text
