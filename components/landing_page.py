import streamlit as st

def show_landing():
    """
    Displays the MentorLink public landing page content (HTML structure only).
    The CSS styling is now handled globally by app.py.
    This version includes a debug comment to help diagnose truncation.
    """
    st.markdown("""<!-- DEBUG START -->
<div class="mentorlink-public">
  <div class="story-section">
    <img src="https://images.unsplash.com/photo-1607387632374-9e9679aa252b?auto=format&fit=crop&w=1600&q=80"
         class="hero-image"
         alt="Mentorship Community Image" />

    <div class="story-container">
      <div class="story-card">
        <h3>🔥 The Match That Sparked a Movement</h3>
        <p><em>I used to feel invisible in the tech space.</em></p>
        <p>Coming from agriculture, I didn’t think I had a seat at the digital table. That changed when I met my mentor — a product manager from The Incubator Hub.</p>

        <p>Now, I’m building my first AI-powered app for farmers in my community. And it all started with one match.</p>
        <p><strong>We don’t just connect mentors and mentees — we build bridges between dreams and destiny.</strong></p>
      </div>

      <div class="story-card">
        <h3>🌱 The Ripple Effect of One Yes</h3>
        <p><strong>The Incubator Hub of Digital SkillUp Africa</strong> launched MentorLink not just as a platform, but a future rewrite.</p>
        <p>Thousands — nurses, accountants, dreamers — started tech with one “yes.”</p>
        <p><strong>It begins with one conversation. One mentor. One belief.</strong></p>
      </div>

      <div class="story-card">
        <h3>🌍 Your World is Changing for Good</h3>
        <p><em>Dear Mentor,</em></p>
        <p>You didn’t just help me code — you helped me believe.</p>
        <p>Today, I build edtech in Northern Nigeria because someone said <strong>“I believe in you.”</strong></p>
        <p><em>Forever grateful,<br>A Fellow, a Builder, a Giver Back</em></p>
      </div>
    </div>

    <div style="text-align: center; margin-top: 2rem;">
      <!-- The "Start Your Journey" button will be rendered by app.py's login function or a dedicated button -->
    </div>

    <div style="text-align: center; margin-top: 2.5rem;">
      <h3>👩🏾‍💻 Are you ready to grow with guidance?</h3>
      <p>Whether breaking into tech or giving back, <strong>MentorLink — powered by The Incubator Hub of Digital SkillUp Africa</strong> — is where growth meets generosity.</p>
      <p>🔹 <strong>Fellows:</strong> Find your mentor. Rewrite your story.<br>
         🔹 <strong>Mentors:</strong> Share your light. Shape the future.</p>
      <p><strong>✨ Impact is just one connection away.</strong></p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
