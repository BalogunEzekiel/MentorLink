import streamlit as st
import time

def show_landing():
    hero_images = [
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//256436-P4QWCA-715.png",
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//women-lift-women_2020-11-23-133503.png",
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//what-is-mentoring1-square.jpg",
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//1.png",
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//2.avif",
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//3.jpg",
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//4.webp",
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//5.webp",
        "https://fzmmeysjrltnktlfkhye.supabase.co/storage/v1/object/public/public-assets//6.jpeg"
    ]

    # Initialize session state
    if "hero_index" not in st.session_state:
        st.session_state.hero_index = 0
    if "fade" not in st.session_state:
        st.session_state.fade = True

    # UI controls
    auto_rotate = st.checkbox("🔁 Auto-rotate images", value=False)
    show_picker = st.checkbox("🎛️ Show image picker", value=False)

    if not auto_rotate:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Previous"):
                st.session_state.hero_index = (st.session_state.hero_index - 1) % len(hero_images)
                st.session_state.fade = False
        with col2:
            if st.button("➡️ Next"):
                st.session_state.hero_index = (st.session_state.hero_index + 1) % len(hero_images)
                st.session_state.fade = False
    else:
        time.sleep(0.5)
        st.session_state.hero_index = (st.session_state.hero_index + 1) % len(hero_images)
        st.session_state.fade = False
        st.experimental_rerun()

    if show_picker:
        selected = st.selectbox("📸 Choose background image:", hero_images, index=st.session_state.hero_index)
        st.session_state.hero_index = hero_images.index(selected)
        st.session_state.fade = False

    selected_image = hero_images[st.session_state.hero_index]
    fade_class = "fade-in" if not st.session_state.fade else ""
    st.session_state.fade = True  # Reset fade to allow animation again

    # Render the full page
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
        opacity: 1;
        transition: opacity 1s ease-in-out;
    }}
    .fade-in {{
        animation: fadeIn 1s;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .hero-overlay {{
        background-color: rgba(0, 0, 0, 0.6);
        padding: 40px;
        color: white;
        text-align: center;
        border-radius: 10px;
        max-width: 80%;
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

    <div class="hero-container {fade_class}">
      <div class="hero-overlay">
        <h1>Mentorship that Moves Mountains</h1>
        <p>From non-tech to tech. From doubt to destiny. MentorLink is where stories begin.</p>
        <div class="hero-buttons">
            <a href="https://mentorlink.streamlit.app/" target="_blank">🚀 Join as a Fellow</a>
            <a href="https://mentorlink.streamlit.app/" target="_blank">✨ Become a Mentor</a>
        </div>
      </div>
    </div>

    <div class="story-container">
      <div class="story-box">
        <h4>🔥 The Match That Sparked a Movement</h4>
        <p><em>I used to feel invisible in the tech space.</em></p>
        <p>Coming from a background in agriculture, I didn’t think someone like me had a seat at the digital table. That changed the moment I met my mentor — a seasoned product manager from The Incubator Hub. He didn’t just teach me tools. He saw potential in me I had buried long ago.</p>
        <p>Today, I’m building my first AI-powered app to help farmers in my community. And it all began with a single mentorship match.</p>
        <p><strong>At MentorLink, we don’t just connect mentors and mentees — we build bridges between dreams and destiny.</strong></p>
      </div>

      <div class="story-box">
        <h4>🌱 The Ripple Effect of One Yes</h4>
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
