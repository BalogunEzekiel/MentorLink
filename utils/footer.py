import streamlit as st

def app_footer():
    st.markdown("---")
    st.markdown("### 🤝 Supporters", unsafe_allow_html=True)

    logos = [
        "assets/BosunTijani1.jpg",
        "assets/Partner_3MTT.png",
        "assets/Partner_NITDA.jpg",
        "assets/Partner_DSN.png",
        "assets/Partner_DeepTech_Ready.png",
        "assets/Partner_Incubator.png",
        "assets/Partner_DSA.jpg",
        "assets/Partner_Google3.png",
        "assets/Partner_Microsoft2.png"
    ]

    for i in range(0, len(logos), 4):
        cols = st.columns(4)
        for j, logo in enumerate(logos[i:i+4]):
            with cols[j]:
                try:
                    st.image(logo, width=120)
                except Exception as e:
                    st.warning(f"Could not load logo: {e}")
