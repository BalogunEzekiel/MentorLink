import streamlit as st
import os

def app_footer():
    st.markdown("---")
    st.markdown("## 🤝 Supporters", unsafe_allow_html=True)

    asset_dir = "assets"
    logos = [
        "Partner_Incubator.png",
        "Partner_DSA.jpg",
    ]

    for i in range(0, len(logos), 4):
        cols = st.columns(4)
        for j, logo in enumerate(logos[i:i+4]):
            with cols[j]:
                path = os.path.join(asset_dir, logo)
                try:
                    st.image(path, width=120)
                except Exception as e:
                    st.warning(f"Could not load logo: {logo}")
