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

        # Scrollable chat container
        st.markdown("""
        <style>
            #mentor-chat-box {
                height: 300px;
                overflow-y: auto;
                border: 1px solid #ccc;
                padding: 10px;
                background-color: #f9f9f9;
                margin-bottom: 10px;
            }
        </style>
        <div id="mentor-chat-box">
        """, unsafe_allow_html=True)

        # Chat history messages
        for entry in st.session_state.chat_history:
            if entry["sender"] == "user":
                st.markdown(f"<p style='text-align:right; margin:5px;'><b>🧑‍💻 You:</b> {entry['message']}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='text-align:left; margin:5px;'><b>🤖 MentorChat:</b> {entry['message']}</p>", unsafe_allow_html=True)

        # Close scroll container and add auto-scroll anchor
        st.markdown("""
        <div id="bottom-anchor"></div>
        </div>
        <script>
            var chatBox = document.getElementById("mentor-chat-box");
            if (chatBox) {
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        </script>
        """, unsafe_allow_html=True)

        # Chat input function
        def handle_chat():
            user_input = st.session_state.get("mentor_input", "").strip()
            role = st.session_state.get("role", "Guest")
            if user_input:
                st.session_state.chat_history.append({"sender": "user", "message": user_input})
                response = mentorchat(user_input, user_role=role)
                st.session_state.chat_history.append({"sender": "bot", "message": response})
                st.session_state["mentor_input"] = ""

        # Static input at bottom
        st.text_input("Type your message...", key="mentor_input", on_change=handle_chat)
