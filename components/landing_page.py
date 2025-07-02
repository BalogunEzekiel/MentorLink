# components/landing_page.py

import streamlit as st

def show_landing():
    st.markdown("""
    <style>
    .mentorlink-public .story-section {
        background-color: #f7f9fc;
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-top: 2rem;
    }
    .mentorlink-public .story-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: center;
    }
    .mentorlink-public .story-card {
        background-color: white;
        flex: 1;
        min-width: 300px;
        max-width: 400px;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .mentorlink-public .story-card h3 {
        color: #4B8BBE;
        font-size: 1.3rem;
    }
    .mentorlink-public .story-card p {
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .mentorlink-public .hero-image {
        width: 100%;
        border-radius: 10px;
        max-height: 300px;
        object-fit: cover;
        margin-bottom: 1.5rem;
    }
    @media (max-width: 768px) {
        .mentorlink-public .story-container {
            flex-direction: column;
        }
    }
    </style>

    <div class="mentorlink-public">
      <div class="story-section">
        <img src="https://images.unsplash.com/photo-1607387632374-9e9679aa252b?auto=format&fit=crop&w=1600&q=80"
             class="hero-image"
             alt="Mentorship Community Image" />

        <div class="story-container">
          <!-- Hardcoded stories (can be replaced by dynamic) -->
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

        <!-- CTA Button -->
        <div style="text-align: center; margin-top: 2rem;">
          <a href="#" style="
            background-color: #4B8BBE;
            color: white;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            display: inline-block;">
            🚀 Start Your Journey
          </a>
        </div>

        <!-- CTA Section -->
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
