import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64
import os

# 1. Setup
st.set_page_config(page_title="IIHS Kengeri Guide", page_icon="🏫")
st.title("🌿 IIHS Kengeri: Living Lab Guide")

# API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key in Secrets! Go to Advanced Settings > Secrets.")

# 2. Knowledge Base
CAMPUS_DATA = {
    "experimental": {
        "name": "Experimental Building",
        "facts": "Built with CSEB blocks and passive stack-effect cooling. Prototype for net-zero living.",
        "prompt": "You are an IIHS expert. Explain the Experimental Building simply and briefly."
    },
    "stp": {
        "name": "STP",
        "facts": "Recycles campus water for landscaping. Circular economy in action.",
        "prompt": "Explain the IIHS water recycling system briefly."
    }
}

# Site selection
site_key = st.query_params.get("site", "experimental")
site_info = CAMPUS_DATA.get(site_key, CAMPUS_DATA["experimental"])

# 3. Sidebar
st.sidebar.title("Guide Settings")
voice_on = st.sidebar.toggle("Enable Voice Guide 🔊", value=True)
st.subheader(f"📍 Location: {site_info['name']}")

# 4. NATIVE 2026 INPUTS
# st.audio_input is the new official way to record on mobile
audio_value = st.audio_input("Record a question")
text_value = st.chat_input("Or type here...")

# 5. Logic
prompt_input = None
if text_value:
    prompt_input = text_value
elif audio_value:
    prompt_input = audio_value

if prompt_input:
    with st.chat_message("assistant"):
        # We use Gemini 3.1 Flash which handles audio and text natively
        model = genai.GenerativeModel('gemini-3.1-flash')
        
        # Send context + the user's voice/text
        context = f"Context: {site_info['facts']}. Task: {site_info['prompt']}"
        response = model.generate_content([context, prompt_input])
        
        st.markdown(response.text)
        
        # 6. Auto-Play Speech
        if voice_on:
            tts = gTTS(text=response.text, lang='en')
            tts.save("speech.mp3")
            with open("speech.mp3", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                # Browser-native autoplay hack
                audio_html = f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true">'
                st.markdown(audio_html, unsafe_allow_html=True)
            os.remove("speech.mp3")
