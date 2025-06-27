import streamlit as st
import streamlit.components.v1 as components
import json
from utils.mentorchat import mentorchat

def show_mentorchat_widget():
    # Initialize session state
    if "mentorchat_history" not in st.session_state:
        st.session_state.mentorchat_history = []

    st.markdown("<div id='mentorchat-container'></div>", unsafe_allow_html=True)

    # Custom HTML/JS/CSS for draggable chat widget
    components.html(f"""
    <style>
        #mentorchat-box {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            max-height: 500px;
            background-color: white;
            border: 1px solid #ccc;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
            border-radius: 10px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            font-family: Arial, sans-serif;
        }}
        #mentorchat-header {{
            background-color: #228be6;
            color: white;
            padding: 10px;
            border-radius: 10px 10px 0 0;
            cursor: move;
        }}
        #mentorchat-body {{
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            font-size: 14px;
        }}
        .mentorchat-message {{
            margin-bottom: 8px;
        }}
        .mentorchat-user {{
            font-weight: bold;
            color: #222;
        }}
        .mentorchat-bot {{
            color: #444;
        }}
        #mentorchat-input {{
            border-top: 1px solid #ccc;
            padding: 8px;
            display: flex;
        }}
        #mentorchat-input input {{
            flex: 1;
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        #mentorchat-input button {{
            background-color: #228be6;
            color: white;
            border: none;
            padding: 6px 10px;
            margin-left: 5px;
            border-radius: 4px;
            cursor: pointer;
        }}
        #mentorchat-toggle {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #228be6;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 50%;
            cursor: pointer;
            z-index: 9998;
        }}
    </style>

    <script>
        const dragElement = (elmnt) => {{
            let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
            if (document.getElementById(elmnt.id + "-header")) {{
                document.getElementById(elmnt.id + "-header").onmousedown = dragMouseDown;
            }}
            function dragMouseDown(e) {{
                e.preventDefault();
                pos3 = e.clientX;
                pos4 = e.clientY;
                document.onmouseup = closeDragElement;
                document.onmousemove = elementDrag;
            }}
            function elementDrag(e) {{
                e.preventDefault();
                pos1 = pos3 - e.clientX;
                pos2 = pos4 - e.clientY;
                pos3 = e.clientX;
                pos4 = e.clientY;
                elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
                elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
            }}
            function closeDragElement() {{
                document.onmouseup = null;
                document.onmousemove = null;
            }}
        }}

        document.addEventListener("DOMContentLoaded", () => {{
            const chatBox = document.createElement("div");
            chatBox.id = "mentorchat-box";
            chatBox.innerHTML = `
                <div id="mentorchat-header">MentorChat</div>
                <div id="mentorchat-body"></div>
                <div id="mentorchat-input">
                    <input type="text" id="mentorchat-text" placeholder="Ask something..." />
                    <button onclick="submitMentorChat()">Send</button>
                </div>
            `;
            document.body.appendChild(chatBox);
            dragElement(chatBox);

            const toggleBtn = document.createElement("button");
            toggleBtn.id = "mentorchat-toggle";
            toggleBtn.innerHTML = "💬";
            toggleBtn.onclick = () => {{
                chatBox.style.display = (chatBox.style.display === "none") ? "flex" : "none";
            }};
            document.body.appendChild(toggleBtn);
        }});

        const submitMentorChat = () => {{
            const input = document.getElementById("mentorchat-text");
            const body = document.getElementById("mentorchat-body");
            const msg = input.value;
            if (!msg) return;
            const userMessage = `<div class='mentorchat-message'><span class='mentorchat-user'>You:</span> ${msg}</div>`;
            body.innerHTML += userMessage;
            input.value = "";

            // Send message to Streamlit (through a hidden input)
            const hiddenInput = window.parent.document.querySelector("iframe").contentWindow.document.querySelector("input[name='mentorchat_user_input']");
            hiddenInput.value = msg;
            hiddenInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }};
    </script>
    """, height=0)

    # Hidden Streamlit input
    user_input = st.text_input("", key="mentorchat_user_input", label_visibility="collapsed")

    role = st.session_state.get("role", "Public")

    if user_input:
        response = mentorchat(user_input, role)
        st.session_state.mentorchat_history.append(("You", user_input))
        st.session_state.mentorchat_history.append(("MentorChat", response))

    # Pass chat history to frontend to re-render (if needed)
    if st.session_state.mentorchat_history:
        chat_script = "<script>let chatBody = document.getElementById('mentorchat-body');"
        for speaker, msg in st.session_state.mentorchat_history:
            cls = "mentorchat-user" if speaker == "You" else "mentorchat-bot"
            chat_script += f"chatBody.innerHTML += `<div class='mentorchat-message'><span class='{cls}'>{speaker}:</span> {msg}</div>`;"
        chat_script += "chatBody.scrollTop = chatBody.scrollHeight;</script>"

        components.html(chat_script, height=0)
