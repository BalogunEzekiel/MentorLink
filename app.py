import streamlit as st
import sys
import os

# ✅ Ensure local module imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ Set app configuration
st.set_page_config(page_title="MentorLink", layout="wide")

# ✅ Add custom header with styling
st.markdown("""
    <style>
    @font-face {
        font-family: 'ScriptMTBold';
        src: local("Script MT Bold");
    }
    .custom-header {
        font-family: 'ScriptMTBold', cursive, serif;
        font-size: 80px;
        color: #4B8BBE;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.1rem;
        margin-top: -1rem;
    }
    .block-container {
        padding-top: 0.5rem !important;
    }
    </style>

    <div class='custom-header'>MentorLink</div>
    <hr style='margin: 0.2rem 0 0.5rem 0;'>
""", unsafe_allow_html=True)

# ✅ Setup admin on first run
from utils.setup_admin import setup_admin_account
setup_admin_account()

# ✅ Auto-cancel expired mentorship requests
from utils.auto_cancel import cancel_expired_requests
cancel_expired_requests()

# ✅ Import views and handlers
from auth.auth_handler import login, logout
from auth.profile import change_password, profile_form
from components.sidebar import sidebar
from roles import admin, mentor, mentee
from utils.footer import app_footer
from components.mentorchat_widget import mentorchat_widget

# ✅ Always show sidebar
sidebar()

# ✅ Show floating chat
mentorchat_widget()

# 🔐 Auth + Routing
if not st.session_state.get("authenticated", False):
    login()

    # ✅ Public landing page stories section
    st.markdown("""
    <div style="display: flex; gap: 20px; justify-content: space-between; flex-wrap: wrap; margin-top: 2rem;">

      <!-- Story 1 -->
      <div style="flex: 1; min-width: 300px;">
        <h3>🔥 The Match That Sparked a Movement</h3>
        <p><em>I used to feel invisible in the tech space.</em></p>
        <p>Coming from a background in agriculture, I didn’t think someone like me had a seat at the digital table. That changed the moment I met my mentor — a seasoned product manager from The Incubator Hub. He didn’t just teach me tools. He saw potential in me I had buried long ago.</p>
        <p>Today, I’m building my first AI-powered app to help farmers in my community. And it all began with a single mentorship match.</p>
        <p><strong>At MentorLink, we don’t just connect mentors and mentees — we build bridges between dreams and destiny.</strong></p>
        <p>👉 <a href="#">Join as a Fellow</a> or <a href="#">Become a Mentor</a></p>
      </div>

      <!-- Story 2 -->
      <div style="flex: 1; min-width: 300px;">
        <h3>🌱 The Ripple Effect of One Yes</h3>
        <p>When <strong>The Incubator Hub of Digital SkillUp Africa</strong> launched MentorLink, we weren’t just building a platform.</p>
        <p>We were rewriting the future for thousands of curious, courageous Africans from all walks of life — nurses learning frontend, accountants mastering data analysis, and dreamers who simply needed a hand to hold while they crossed into tech.</p>
        <p>Every week, mentors from our curated hub take time to pour their experience into someone ready to learn, lead, and launch.</p>
        <p>The result? More than just job placements. We’re witnessing confidence rise, communities transform, and impact multiply.</p>
        <p><strong>It starts with one conversation. One mentor. One “yes.”</strong></p>
      </div>

      <!-- Story 3 -->
      <div style="flex: 1; min-width: 300px;">
        <h3>🌍 A Letter from a Future Fellow</h3>
        <p><em>Dear Mentor,</em></p>
        <p>You didn’t just help me code.</p>
        <p>You helped me believe.</p>
        <p>Before MentorLink, I was unsure. I kept asking myself if I was too old, too inexperienced, too “non-tech” to start. But you showed up. Week after week. With patience. With real talk. With direction.</p>
        <p>Today, I’m helping build accessible edtech platforms in Northern Nigeria. And it’s all because someone from The Incubator Hub said <strong>“I believe in you.”</strong></p>
        <p>Thank you for not seeing just my past — but my possibility.</p>
        <p><em>Forever grateful,<br>A Fellow, a Builder, a Giver Back</em></p>
      </div>

    </div>

    <hr style="margin-top: 3rem;">

    <!-- CTA Section -->
    <div style="text-align: center;">
      <h3>👩🏾‍💻 Are you ready to grow with guidance?</h3>
      <p>Whether you’re just breaking into tech or you're here to give back, <strong>MentorLink — powered by The Incubator Hub of Digital SkillUp Africa</strong> — is where growth meets generosity.</p>
      <p>🔹 <strong>Fellows:</strong> Find your mentor. Rewrite your story.<br>
         🔹 <strong>Mentors:</strong> Share your light. Shape the future.</p>
      <p><strong>✨ Impact is just one connection away.</strong></p>
    </div>
    """, unsafe_allow_html=True)

else:
    role = st.session_state.get("role")
    user = st.session_state.get("user", {})

    if role != "Admin":
        if user.get("must_change_password", False):
            change_password()
        elif not user.get("profile_completed", False):
            profile_form()
        else:
            if role == "Mentor":
                mentor.show()
            elif role == "Mentee":
                mentee.show()
            else:
                st.warning("⚠️ Unknown role.")
    else:
        admin.show()

# 🧾 Footer on public page
if not st.session_state.get("authenticated", False):
    app_footer()

# 🔁 Rerun if needed
if st.session_state.get("do_rerun"):
    st.session_state["do_rerun"] = False
    st.rerun()
