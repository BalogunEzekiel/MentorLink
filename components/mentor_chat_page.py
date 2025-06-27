# Mocking Streamlit components for simulation
class MockStreamlit:
    def __init__(self):
        self.session_state = {}
        self.chat_messages = []
        self._user_input_queue = []
        self._rerun_called = False
        self._placeholders = {} # To simulate st.empty()

    def markdown(self, text):
        print(f"\n--- Markdown Output ---\n{text}\n-----------------------")

    def chat_input(self, prompt):
        if self._user_input_queue:
            return self._user_input_queue.pop(0)
        return None # No input yet

    def chat_message(self, name):
        class ChatMessageContext:
            def __enter__(self_ctx):
                print(f"\n[{name.upper()}]:")
            def __exit__(self_ctx, exc_type, exc_val, exc_tb):
                pass
        return ChatMessageContext()

    def write(self, text):
        print(text)

    def rerun(self):
        self._rerun_called = True
        # In a real Streamlit app, this would re-execute the script from top
        # For simulation, we'll indicate it and then re-run our show_mentor_chat logic.

    def empty(self):
        # Simulates st.empty() for typing animation
        class EmptyPlaceholder:
            def __init__(self_placeholder):
                self_placeholder.content = ""
            def markdown(self_placeholder, text):
                self_placeholder.content = text
                # In a real app, this updates the UI. Here, we just print the effect.
                # We'll handle the actual printing in the simulate_typing function
                pass
        placeholder_id = len(self._placeholders)
        self._placeholders[placeholder_id] = EmptyPlaceholder()
        return self._placeholders[placeholder_id]

# Mocking time for typing simulation
class MockTime:
    def sleep(self, seconds):
        # In a real scenario, this pauses. Here, we just acknowledge it.
        pass

# Mocking mentorchat function
def mock_mentorchat(user_input, user_role="Public"):
    print(f"\n[MENTORCHAT FUNCTION CALL] Input: '{user_input}', Role: '{user_role}'")
    if user_input.lower() == "hello":
        return "Hello there! How can I assist you today?"
    elif "help" in user_input.lower():
        return "I can help with various topics related to your role. What specifically do you need assistance with?"
    else:
        return f"Thanks for your message, '{user_input}'. I'm MentorChat, ready to guide you!"

# Assign mocks
st = MockStreamlit()
time = MockTime()
mentorchat = mock_mentorchat

# --- Original functions (copied directly) ---
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
                    simulate_typing(message)  # Typing simulation only for latest
                else:
                    st.write(message)

# 🔄 Typing Simulation
def simulate_typing(response: str, delay: float = 0.02):
    displayed = ""
    message_placeholder = st.empty() # This returns our mocked placeholder

    print("\n[ASSISTANT]: (Typing simulation starts)")
    for i, char in enumerate(response):
        displayed += char
        # In a real Streamlit app, message_placeholder.markdown updates the UI
        # Here, we'll print the effect.
        if i % 5 == 0 or i == len(response) - 1: # Print every 5 chars or at the end
            print(f"\r{displayed}▌", end="")
        time.sleep(delay)
    print(f"\r{displayed}") # Final text
    print("(Typing simulation ends)")

# --- Simulation Execution ---

print("--- Start of Streamlit App Simulation ---")

# Step 1: Initial load of the app
print("\n=== App Load (First Run) ===")
show_mentor_chat()
print(f"\nSession State after initial load: {st.session_state}")

# Step 2: User types "Hello" and presses Enter
print("\n\n=== User Input: 'Hello' ===")
st._user_input_queue.append("Hello")
st._rerun_called = False # Reset rerun flag for this simulation step
show_mentor_chat()
print(f"\nSession State after user input (before first rerun): {st.session_state}")
print(f"Rerun called: {st._rerun_called}")

# Streamlit reruns
if st._rerun_called:
    print("\n\n=== Rerun 1 (After User Input, Before Bot Processing) ===")
    st._rerun_called = False # Reset for the next potential rerun
    show_mentor_chat()
    print(f"\nSession State after Rerun 1 (during bot processing): {st.session_state}")
    print(f"Rerun called: {st._rerun_called}")

# Streamlit reruns again after bot response is generated
if st._rerun_called:
    print("\n\n=== Rerun 2 (After Bot Response Generated, Displaying with Typing) ===")
    st._rerun_called = False # Reset for future interactions
    show_mentor_chat()
    print(f"\nSession State after Rerun 2 (displaying final response): {st.session_state}")
    print(f"Rerun called: {st._rerun_called}")

print("\n--- End of Streamlit App Simulation ---")
