import streamlit as st
import requests

BACKEND_API = "http://backend:8010"

st.title("🔐 Login")

# Clear session if user asks to log out
if st.session_state.get("auth") and st.button("Logout"):
    st.session_state.pop("auth", None)
    st.success("Logged out.")
    st.stop()

role = st.selectbox("I am a", ["patient", "carer"])
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    try:
        resp = requests.post(
            f"{BACKEND_API}/patients/login",
            json={
                "role": role,
                "username": username,
                "password": password,
            },
            timeout=8,
        )
        if resp.status_code != 200:
            detail = resp.json().get("detail", "Invalid credentials")
            st.error(detail)
        else:
            st.session_state.auth = resp.json()
            st.success("Login successful. Go to Patient Profile to view records.")
    except Exception as e:
        st.error(str(e))

# Show current session
auth = st.session_state.get("auth")
if auth:
    st.info(f"Logged in as {auth['user']['full_name']} ({auth['role']}).")
    patients = auth.get("patients", [])
    if patients:
        st.write("Accessible patients:")
        for p in patients:
            st.write(f"- {p['full_name']} (ID: {p['id']})")
    else:
        st.warning("No patients linked to this account.")
