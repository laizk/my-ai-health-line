import streamlit as st
import requests
from auth_utils import persist_auth, hydrate_auth_from_params, clear_auth
from config import AUTH_LOGIN_API

st.title("🏥 My AI Health Line")

# Restore session from token if present (browser refresh)
hydrate_auth_from_params()
auth = st.session_state.get("auth")

if auth:
    st.success(f"Already logged in as {auth['user']['full_name']} ({auth['role']}).")
    if st.button("Logout"):
        clear_auth()
        st.rerun()
else:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log In"):
        try:
            resp = requests.post(
                AUTH_LOGIN_API,
                json={
                    "username": username,
                    "password": password,
                },
                timeout=8,
            )
            if resp.status_code != 200:
                detail = resp.json().get("detail", "Invalid credentials")
                st.error(detail)
            else:
                persist_auth(resp.json())
                st.rerun()
        except Exception as e:
            st.error(str(e))
