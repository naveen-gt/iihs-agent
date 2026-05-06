import streamlit as st
import google.generativeai as genai
from streamlit_TTS import text_to_speech

# 1. Setup the Vibe
st.set_page_config(page_title="IIHS Kengeri Guide", page_icon="🏫", layout="centered")
st.title("🌿 IIHS Kengeri: Living Lab Guide")

# 2. Sidebar Settings
st.sidebar.title("Settings")
voice_on = st.sidebar.toggle("Enable Voice Guide 🔊", value=True)

# API Key Configuration
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Please add your Gemini API Key in Streamlit Secrets!")

# 3. Knowledge Base (Experimental Building + STP)
CAMPUS_DATA = {
    "experimental": {
        "name": "Experimental Building (Living Lab)",
        "facts": """
            The Experimental Building is a 'Living Lab' prototype for net-zero carbon campus living. 
            - Built using Compressed Stabilized Earth Blocks (CSEB) from local soil.
            - Passive Design: Uses the 'Stack Effect' for ventilation (hot air exits top, cool air draws in).
            - Cooling: High thermal mass walls regulate temperature naturally.
            - Labs: Houses IIHS Environmental Lab, Media Lab, and IoT Lab.
        """,
        "prompt": "You are a senior researcher at IIHS. Explain the Experimental Building's sustainability simply. Keep it short for a tour."
    },
    "stp": {
        "name": "Wastewater Treatment (STP)",
        "facts": """
            Decentralized circular water system.
            - Objective: Near net-zero municipal water use.
            - Process: Biological treatment for recycling water for landscaping.
        """,
        "prompt": "You are a water engineer at IIHS. Explain the circular water economy briefly."
    }
}

# Detect location from URL (?site=experimental)
query_params = st.query_params
current_site_key = query_params.get("site", "experimental")
site_info = CAMPUS_DATA.get(current_site_key, CAMPUS_DATA["experimental"])

st.subheader(f"📍 Location: {site_info['name']}")
st.info(site_info['facts'])

# 4. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input: Native 2026 Microphone + Text
if prompt := st.chat_input("Ask or tap the mic...", accept_audio=True):
    
    # Check if input was voice or text
    user_text = prompt.text if isinstance(prompt, dict) else prompt

    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # 5. Agent Response using Gemini 3.1 Flash
    with st.chat_message("assistant"):
        # Updated to May 2026 stable model
        model = genai.GenerativeModel('gemini-3.1-flash')
        
        full_prompt = f"{site_info['prompt']}. Site Facts: {site_info['facts']}. Question: {user_text}"
        response = model.generate_content(full_prompt)
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # 6. Audio Playback (If enabled)
        if voice_on:
            text_to_speech(response.text, language='en')

# 7. Vision Feature
with st.expander("📸 Identify a Feature"):
    img_file = st.camera_input("Take a photo of a building component")
    if img_file:
        model_vision = genai.GenerativeModel('gemini-3.1-flash')
        img_bytes = img_file.getvalue()
        res = model_vision.generate_content([
            "Identify this IIHS campus feature and explain its sustainability value briefly.",
            {"mime_type": "image/jpeg", "data": img_bytes}
        ])
        st.write(res.text)
        if voice_on:
            text_to_speech(res.text, language='en')
