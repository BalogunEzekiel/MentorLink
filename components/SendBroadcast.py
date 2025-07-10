import streamlit as st
from supabase import create_client
from datetime import datetime
import uuid

# Connect to Supabase
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📢 Admin: Send Broadcast Message")

if st.session_state.get("user_role") != "ADMIN":
    st.error("Access Denied. Admins only.")
    st.stop()

title = st.text_input("Message Title")
body = st.text_area("Message Body")
target = st.selectbox("Send To", ["All Users", "Mentors", "Mentees", "Individual"])

receiver_id = None
role = None

if target == "Individual":
    user_email = st.text_input("Enter User Email")
    if user_email:
        user = supabase.table("users").select("userid").eq("email", user_email).execute().data
        if user:
            receiver_id = user[0]["userid"]
        else:
            st.warning("User not found")

elif target == "Mentors":
    role = "MENTOR"
elif target == "Mentees":
    role = "MENTEE"

if st.button("📤 Send Message"):
    if not title or not body:
        st.warning("Please provide both title and body.")
    else:
        message_data = {
            "id": str(uuid.uuid4()),
            "sender_id": st.session_state.get("user_id"),
            "receiver_id": receiver_id,
            "role": role,
            "title": title,
            "body": body,
            "created_at": datetime.now().isoformat(),
            "is_read": False
        }
        supabase.table("messages").insert(message_data).execute()
        st.success("Message sent successfully!")
