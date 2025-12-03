import streamlit as st
import requests
import time
from config import DOCTOR_ASK_API
from auth_utils import hydrate_auth_from_params

# Restore auth
hydrate_auth_from_params()
auth = st.session_state.get("auth")
role = auth.get("role") if auth else None

st.title("Doctor AI Assistant")

if role != "doctor":
    st.error("This assistant is for doctors only. Please log in as a doctor.")
    st.stop()

# Simple chat history and session tracking
if "doctor_ai_messages" not in st.session_state:
    st.session_state.doctor_ai_messages = []
if "doctor_ai_session_id" not in st.session_state:
    st.session_state.doctor_ai_session_id = None

for msg in st.session_state.doctor_ai_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask the Doctor AI..."):
    st.session_state.doctor_ai_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            for i in range(6):
                dots = "." * ((i % 3) + 1)
                placeholder.markdown(f"⏳ *Thinking{dots}*")
                time.sleep(0.3)

            resp = requests.post(
                DOCTOR_ASK_API,
                json={
                    "prompt": prompt,
                    "user_name": auth["user"]["username"] if auth else None,
                    "session_id": st.session_state.doctor_ai_session_id,
                },
                timeout=30,
            )
            data = resp.json()
            st.session_state.doctor_ai_session_id = data.get("session_id", st.session_state.doctor_ai_session_id)
            # Response may be structured; attempt to extract text
            raw = data.get("response", "")
            if isinstance(raw, list):
                text = raw[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            else:
                text = raw
            placeholder.empty()
            st.markdown(text)
            # Prefer backend history to avoid duplicates
            backend_history = data.get("history")
            if backend_history:
                st.session_state.doctor_ai_messages = backend_history
            else:
                # prevent duplicate consecutive assistant messages
                if not st.session_state.doctor_ai_messages or st.session_state.doctor_ai_messages[-1]["content"] != text:
                    st.session_state.doctor_ai_messages.append({"role": "assistant", "content": text})
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
    except Exception as e:
        st.error(f"Request failed: {e}")
