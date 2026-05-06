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
# 3. Define the Campus Knowledge (Deepened with IIHS Knowledge Gateway Data)
CAMPUS_DATA = {
    "experimental": {
        "name": "Experimental Building (Living Lab)",
        "facts": """
            The Experimental Building is a 'Living Lab' prototype for net-zero carbon campus living. 
            Key features: 
            - Construction: Built using Compressed Stabilized Earth Blocks (CSEB) made from local soil to reduce carbon footprint.
            - Passive Design: Uses the 'Stack Effect' for ventilation (hot air exits top vents, drawing cool air in).
            - Cooling: High thermal mass walls regulate temperature naturally.
            - Labs: Houses the IIHS Environmental Lab, Media Lab, and the Internet of Things (IoT) Lab.
            - Architecture: Designed to test modularity for the rest of the 54-acre Kengeri campus.
        """,
        "prompt": """
            You are a senior researcher at the IIHS Kengeri Campus. 
            Use these core principles in your explanation:
            1. Passive Building Design (Natural light/air).
            2. Materiality (Low embodied carbon in earth blocks).
            3. Monitoring (How the labs measure heat and energy).
            Be technical but accessible to students. Mention that this building was a prototype for the whole campus.
        """
    },
    "stp": {
        "name": "Wastewater Treatment (STP)",
        "facts": """
            The Kengeri campus uses a decentralized circular water system.
            - Objective: Near net-zero municipal water use.
            - Process: Uses biological treatment to recycle wastewater for landscaping and agriculture.
            - Research: Part of the 'Flowing towards Sustainability' study on campus water management.
        """,
        "prompt": "You are a water systems engineer. Explain the circular water economy at IIHS."
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
        model = genai.GenerativeModel('gemini-3-flash-preview')
        full_context = f"{site_info['prompt']}. Context: {site_info['facts']}. Question: {prompt}"
        response = model.generate_content(full_context)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# 6. Bonus: The "Vision" Feature (Let students take a photo)
with st.expander("📸 Identify a Feature (Experimental)"):
    img_file = st.camera_input("Take a photo of a building component")
    if img_file:
        model_vision = genai.GenerativeModel('gemini-3-flash-preview')
        img_bytes = img_file.getvalue()
        # Vibe coding the vision prompt
        res = model_vision.generate_content([
            "Identify what part of the sustainable building this is and why it matters.",
            {"mime_type": "image/jpeg", "data": img_bytes}
        ])
        st.write(res.text)
