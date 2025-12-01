import streamlit as st
import requests
import time
import json

BACKEND_API_URL = "http://backend:8010/ask"

# -------------------------------
# Typing animation function
# -------------------------------
def type_writer(text, container, speed=0.02):
    typed = ""
    for char in text:
        typed += char
        container.markdown(typed)
        time.sleep(speed)

# -------------------------------
# Initialize chat history
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Concierge AI Assistant")

# Render all previous messages from history **first**
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------------
# Handle user input
# -------------------------------
if prompt := st.chat_input("What is up?"):

    # --- 1. Add + display user message ---
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # --- 2. Create a placeholder for animated assistant message ---
        with st.chat_message("assistant"):
            animated_placeholder = st.empty()

            # Loader animation
            for i in range(6):
                dots = "." * ((i % 3) + 1)
                animated_placeholder.markdown(f"⏳ *Thinking{dots}*")
                time.sleep(0.3)

            # Backend call
            response = requests.post(
                BACKEND_API_URL,
                json={"prompt": prompt},
                timeout=12
            )
            data = response.json()

            response_text = (
                data.get("response", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
            )

            # Clear loader animation for clean typewriter text
            animated_placeholder.empty()

            # Typewriter effect ONLY on this placeholder
            type_writer(response_text, animated_placeholder)

        # --- 3. SAVE the assistant message into chat history ---
        st.session_state.messages.append({"role": "assistant", "content": response_text})

        # --- IMPORTANT FIX ---
        # Immediately rerun so chatting starts fresh without keeping animation output
        st.rerun()

    except Exception as e:
        st.error("Request failed.")
        st.exception(e)
