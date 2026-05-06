import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64

# 1. Setup
st.set_page_config(page_title="IIHS Kengeri Guide", page_icon="🏫")
st.title("🌿 IIHS Kengeri: Living Lab Guide")

# API Key
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key in Secrets!")

# 2. Knowledge Base
CAMPUS_DATA = {
    "experimental": {
        "name": "Experimental Building",
        "facts": "Built with CSEB blocks and passive stack-effect cooling.",
        "prompt": "You are an IIHS expert. Explain the Experimental Building simply."
    },
    "stp": {
        "name": "STP",
        "facts": "Recycles campus water for landscaping.",
        "prompt": "Explain the IIHS water recycling system."
    }
}

site_info = CAMPUS_DATA.get(st.query_params.get("site", "experimental"), CAMPUS_DATA["experimental"])

# 3. Voice Toggle
voice_on = st.sidebar.toggle("Enable Voice Guide 🔊", value=True)

# 4. NEW 2026 NATIVE VOICE INPUT
st.write("### Ask a Question")
# This is the new way: no extra libraries needed
audio_input = st.audio_input("Record your question") 
text_input = st.chat_input("Or type here...")

# 5. Logic to handle either Voice or Text
prompt = None
if text_input:
    prompt = text_input
elif audio_input:
    # In 2026, Gemini can 'hear' the audio file directly!
    prompt = audio_input

if prompt:
    with st.chat_message("user"):
        st.write("Processing your request...")
    
    with st.chat_message("assistant"):
        model = genai.GenerativeModel('gemini-3.1-flash')
        # We send the text or audio directly to Gemini
        response = model.generate_content([f"Context: {site_info['facts']}. Task: {site_info['prompt']}", prompt])
        st.markdown(response.text)
        
        # 6. Simple Text-to-Speech (The Vibe Way)
        if voice_on:
            tts = gTTS(text=response.text, lang='en')
            tts.save("response.mp3")
            with open("response.mp3", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
                st.markdown(md, unsafe_allow_body=True)
