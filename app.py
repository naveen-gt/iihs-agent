import streamlit as st
import google.generativeai as genai

# 1. Setup the Vibe
st.set_page_config(page_title="IIHS Kengeri Guide", page_icon="🏫")
st.title("🌿 IIHS Kengeri: Living Lab Guide")

# 2. Get your Free API Key from secrets (Streamlit Cloud handles this)
# For local testing, you can just paste your key here: genai.configure(api_key="YOUR_KEY_HERE")
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Please add your Gemini API Key!")

# 3. Define the Campus Knowledge (The "Vibe" Data)
CAMPUS_DATA = {
    "experimental": {
        "name": "Experimental Building",
        "facts": "Uses CSEB (Compressed Stabilized Earth Blocks), passive cooling, stack effect ventilation, and local soil construction.",
        "prompt": "You are an expert architect at IIHS. Explain the Experimental Building's sustainability features simply."
    },
    "stp": {
        "name": "Sewage Treatment Plant (STP)",
        "facts": "Decentralized system, treats campus wastewater for landscaping, uses biological processes.",
        "prompt": "You are an environmental engineer. Explain how this STP turns waste into a resource."
    }
}

# 4. Detect location from the URL (e.g., app.url/?site=experimental)
query_params = st.query_params
current_site_key = query_params.get("site", "experimental") # Defaults to experimental
site_info = CAMPUS_DATA.get(current_site_key)

st.subheader(f"📍 You are at: {site_info['name']}")
st.info(site_info['facts'])

# 5. The Agent Interaction
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask me anything about this spot..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent Response Logic
    with st.chat_message("assistant"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_context = f"{site_info['prompt']}. Context: {site_info['facts']}. Question: {prompt}"
        response = model.generate_content(full_context)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# 6. Bonus: The "Vision" Feature (Let students take a photo)
with st.expander("📸 Identify a Feature (Experimental)"):
    img_file = st.camera_input("Take a photo of a building component")
    if img_file:
        model_vision = genai.GenerativeModel('gemini-1.5-flash')
        img_bytes = img_file.getvalue()
        # Vibe coding the vision prompt
        res = model_vision.generate_content([
            "Identify what part of the sustainable building this is and why it matters.",
            {"mime_type": "image/jpeg", "data": img_bytes}
        ])
        st.write(res.text)