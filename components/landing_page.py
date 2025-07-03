import streamlit as st
import random

def show_landing():
    hero_images = [
#        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//256436-P4QWCA-715.png",
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//women-lift-women_2020-11-23-133503.png"
#        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//what-is-mentoring1-square.jpg"
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//1.png"
    ]
    selected_image = random.choice(hero_images)

    st.markdown(f"""
    <style>
    .hero-container {{
        position: relative;
        width: 100%;
        height: 420px;
        background-image: url('{selected_image}');
        background-size: cover;
        background-position: center;
        border-radius: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 3rem;
    }}
    .hero-overlay {{
        background-color: rgba(0, 0, 0, 0.6);
        padding: 40px;
        color: white;
        text-align: center;
        border-radius: 10px;
        max-width: 80%;
    }}
    .hero-overlay h1 {{
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    .hero-overlay p {{
        font-size: 18px;
        margin-bottom: 20px;
    }}
    .hero-buttons a {{
        margin: 5px 10px;
        padding: 10px 20px;
        background-color: #4B8BBE;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
    }}
    .hero-buttons a:hover {{
        background-color: #366fa1;
    }}

    .story-container {{
        display: flex;
        gap: 20px;
        justify-content: space-between;
        flex-wrap: wrap;
        margin-top: 2rem;
    }}
    .story-box {{
        flex: 1;
        min-width: 300px;
        background-color: #f5f9ff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }}
    .cta-box {{
        background-color: #e0f7ea;
        border-radius: 10px;
        padding: 30px;
        margin-top: 3rem;
        text-align: center;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }}
    </style>

    <div class="hero-container">
      <div class="hero-overlay">
        <h1>Mentorship that Moves Mountains</h1>
        <p>From non-tech to tech. From doubt to destiny. MentorLink is where stories begin.</p>
        <div class="hero-buttons">
            <a href="#">🚀 Join as a Fellow</a>
            <a href="#">✨ Become a Mentor</a>
        </div>
      </div>
    </div>

    <div class="story-container">
      <div class="story-box">
        <h3.5>🔥 The Match That Sparked a Movement</h3.5>
        <p><em>I used to feel invisible in the tech space.</em></p>
        <p>Coming from a background in agriculture, I didn’t think someone like me had a seat at the digital table. That changed the moment I met my mentor — a seasoned product manager from The Incubator Hub. He didn’t just teach me tools. He saw potential in me I had buried long ago.</p>
        <p>Today, I’m building my first AI-powered app to help farmers in my community. And it all began with a single mentorship match.</p>
        <p><strong>At MentorLink, we don’t just connect mentors and mentees — we build bridges between dreams and destiny.</strong></p>
        <p>
          <a href="#" style="background:#4B8BBE;color:white;padding:8px 16px;border-radius:5px;text-decoration:none;">Join as a Fellow</a> 
          &nbsp;
          <a href="#" style="background:#00a76f;color:white;padding:8px 16px;border-radius:5px;text-decoration:none;">Become a Mentor</a>
        </p>
      </div>

      <div class="story-box">
        <h3.5>🌱 The Ripple Effect of One Yes</h3.5>
        <p>When <strong>The Incubator Hub of Digital SkillUp Africa</strong> launched MentorLink, we weren’t just building a platform.</p>
        <p>We were rewriting the future for thousands of curious, courageous Africans — nurses learning frontend, accountants mastering data analysis, and dreamers who needed a hand to cross into tech.</p>
        <p>Mentors from our curated hub take time each week to pour their experience into someone ready to learn, lead, and launch.</p>
        <p><strong>It starts with one conversation. One mentor. One “yes.”</strong></p>
      </div>

      <div class="story-box">
        <h4>🌍 Your World is Changing for Good</h4>
        <p><em>Dear Mentor,</em></p>
        <p>You didn’t just help me code. You helped me believe.</p>
        <p>Before MentorLink, I was unsure. I kept asking if I was too old, too non-tech to start. But you showed up. With patience. With direction.</p>
        <p>Today, I’m helping build accessible edtech platforms in Northern Nigeria. And it’s because someone from The Incubator Hub said “I believe in you.”</p>
        <p><em>Forever grateful,<br>A Fellow, a Builder, a Giver Back</em></p>
      </div>
    </div>

    <div class="cta-box">
      <h4>👩🏾‍💻 Are you ready to grow with guidance?</h4>
      <p>Whether you’re just breaking into tech or you're here to give back, <strong>MentorLink — powered by The Incubator Hub of Digital SkillUp Africa</strong> — is where growth meets generosity.</p>
      <p>🔹 <strong>Fellows:</strong> Find your mentor. Rewrite your story.<br>
         🔹 <strong>Mentors:</strong> Share your light. Shape the future.</p>
      <p><strong>✨ Impact is just one connection away.</strong></p>
    </div>
    """, unsafe_allow_html=True)
