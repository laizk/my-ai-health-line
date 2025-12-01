import streamlit as st
import requests
import time
import json

from config import ASK_API, ASK_HISTORY_BY_USER_API
from auth_utils import hydrate_auth_from_params

# Restore auth
hydrate_auth_from_params()
auth = st.session_state.get("auth")

current_user = "guest_user"
if auth:
    user_info = auth.get("user", {})
    current_user = user_info.get("username") or user_info.get("full_name") or "guest_user"

# When user changes, reset local cache (history reloads by user)
if st.session_state.get("last_user") != current_user:
    st.session_state.messages = []
    st.session_state.last_user = current_user

st.title("Concierge AI Assistant")
if not auth:
    st.info("You are chatting as a guest. Please login from the Login page for a personalized experience, but you can continue chatting.")


def type_writer(text, container, speed=0.02):
    """Simple typewriter effect for assistant responses."""
    typed = ""
    for char in text:
        typed += char
        container.markdown(typed)
        time.sleep(speed)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


def load_history():
    """Load history by user_id (single thread)."""
    try:
        resp = requests.get(
            ASK_HISTORY_BY_USER_API,
            params={"user_id": current_user},
            timeout=6,
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.messages = data.get("history", [])
    except Exception:
        pass


# Load history for current user
load_history()

# Render existing history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Chat with the Concierge AI Assistant..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            animated_placeholder = st.empty()
            for i in range(6):
                dots = "." * ((i % 3) + 1)
                animated_placeholder.markdown(f"⏳ *Thinking{dots}*")
                time.sleep(0.3)

            user_name = current_user

            response = requests.post(
                ASK_API,
                json={
                    "prompt": prompt,
                    "user_name": user_name,
                },
                timeout=12,
            )
            data = response.json()

            raw_response = data.get("response", "")
            if isinstance(raw_response, list):
                response_text = (
                    raw_response[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
            else:
                response_text = raw_response or ""

            animated_placeholder.empty()
            type_writer(response_text, animated_placeholder)

        backend_history = data.get("history")
        if backend_history:
            st.session_state.messages = backend_history
        else:
            st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error("Request failed.")
        st.exception(e)
