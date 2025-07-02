import streamlit as st

def show_landing():
    """
    Displays the MentorLink public landing page content.
    This function is purely for presentation, as navigation and authentication
    are handled by the main app.py file.
    """
    # Ensure the entire HTML, including <style> and outer divs, is within the markdown string.
    st.markdown("""
<style>
/* General styling for the MentorLink public section */
.mentorlink-public .story-section {
    background-color: #f7f9fc; /* Light grey background for the section */
    padding: 2rem 1rem; /* Padding around the content */
    border-radius: 10px; /* Rounded corners for the section */
    margin-top: 2rem; /* Top margin for spacing */
}
/* Container for story cards, using flexbox for layout */
.mentorlink-public .story-container {
    display: flex; /* Enable flexbox */
    flex-wrap: wrap; /* Allow items to wrap to the next line */
    gap: 20px; /* Space between flex items */
    justify-content: center; /* Center items horizontally */
}
/* Styling for individual story cards */
.mentorlink-public .story-card {
    background-color: white; /* White background for cards */
    flex: 1; /* Allow cards to grow and shrink */
    min-width: 300px; /* Minimum width for cards */
    max-width: 400px; /* Maximum width for cards */
    padding: 1.5rem; /* Padding inside cards */
    border-radius: 8px; /* Rounded corners for cards */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); /* Subtle shadow for depth */
}
/* Heading styling within story cards */
.mentorlink-public .story-card h3 {
    color: #4B8BBE; /* Specific blue color for headings */
    font-size: 1.3rem; /* Font size for headings */
}
/* Paragraph styling within story cards */
.mentorlink-public .story-card p {
    line-height: 1.6; /* Line height for readability */
    font-size: 0.95rem; /* Font size for paragraphs */
}
/* Styling for the main hero image */
.mentorlink-public .hero-image {
    width: 100%; /* Full width of its container */
    border-radius: 10px; /* Rounded corners for the image */
    max-height: 300px; /* Maximum height to prevent it from being too tall */
    object-fit: cover; /* Cover the area, cropping if necessary */
    margin-bottom: 1.5rem; /* Bottom margin for spacing */
}
/* Responsive design: Stack story cards vertically on smaller screens */
@media (max-width: 768px) {
    .mentorlink-public .story-container {
        flex-direction: column; /* Stack items vertically */
    }
}
</style>

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
      <!-- The "Start Your Journey" button will be rendered by app.py using st.button for functionality -->
      <!-- This HTML comment is to indicate where a Streamlit button would conceptually go if this were standalone -->
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
