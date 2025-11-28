import streamlit as st
import requests

BACKEND_API = "http://backend:8010"

st.set_page_config(page_title="MyAIHealthLine", page_icon="🏥")

st.title("🏥 MyAIHealthLine Dashboard")
auth = st.session_state.get("auth")

if auth:
    st.success(f"Logged in as {auth['user']['full_name']} ({auth['role']}).")
    patients = auth.get("patients", [])
    if patients:
        st.write("Accessible patients:")
        for p in patients:
            st.write(f"- {p['full_name']} (ID: {p['id']})")
        st.page_link("pages/patient_profile.py", label="Open Patient Profile")
    else:
        st.warning("No patients linked to this account.")

    if st.button("Logout"):
        st.session_state.pop("auth", None)
        st.success("Logged out.")
else:
    st.subheader("🔐 Login")
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
                st.rerun()
        except Exception as e:
            st.error(str(e))
