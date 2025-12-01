import streamlit as st
import requests
from pathlib import Path
from auth_utils import hydrate_auth_from_params, clear_auth

st.set_page_config(page_title="MyAIHealthLine", page_icon="🏥")

# Hydrate session auth from token in query params if present
hydrate_auth_from_params()

# ============================================================
# GLOBAL LOGOUT BUTTON (VISIBLE ON ALL PAGES)
# ============================================================
def render_global_logout_button():
    auth = st.session_state.get("auth")
    if not auth:
        return

    user_info = auth.get("user", {})
    display_name = user_info.get("full_name") or user_info.get("username") or "User"
    role_label = auth.get("role", "")

    # CSS for positioning the logout button at top-right
    st.markdown("""
        <style>
            .logout-container {
                position: fixed;
                top: 15px;
                right: 20px;
                z-index: 1000;
                background: rgba(255, 255, 255, 0.0);
            }
            .logout-user {
                font-size: 14px;
                margin-right: 12px;
            }
        </style>
    """, unsafe_allow_html=True)

    # HTML container with logout button
    st.markdown('<div class="logout-container">', unsafe_allow_html=True)

    # Show username + logout button
    col1, col2 = st.columns([0.75, 0.25])

    with col1:
        st.markdown(
            f"<div class='logout-user'>👤 {display_name} ({role_label})</div>",
            unsafe_allow_html=True
        )

    with col2:
        if st.button("🔓 Logout"):
            clear_auth()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# Render logout button globally
render_global_logout_button()
# ============================================================


# ============================================================
# PAGE DEFINITIONS
# ============================================================
page_login = st.Page("pages/account/login.py", title="Login", icon=":material/home:")
page_admin = st.Page("pages/admin/admin.py", title="Admin", icon=":material/home:")
page_ai_assistant = st.Page(
    "pages/ai/concierge_ai_assistant.py", title="Concierge AI", icon=":material/cognition_2:"
)
page_doctor = st.Page("pages/doctor/doctor.py", title="Patient Information", icon=":material/search:")
page_patient_profile = st.Page(
    "pages/patient/patient_profile.py", title="Patient Profile", icon=":material/history:"
)

auth = st.session_state.get("auth")
app_root = Path(__file__).parent

# ============================================================
# NAVIGATION BASED ON LOGIN STATUS
# ============================================================

if auth:
    # Logged-in navigation
    role = auth.get("role")
    nav_map = {}
    if role in {"patient", "carer"}:
        nav_map = {
            "Account": [page_patient_profile],
            "AI": [page_ai_assistant],
        }
    elif role == "doctor":
        nav_map = {
            "Doctor": [page_doctor, page_patient_profile],
            "AI": [page_ai_assistant],
        }
    elif role == "admin":
        nav_map = {
            "Admin": [page_admin, page_patient_profile, page_doctor],
            "AI": [page_ai_assistant],
        }
    else:
        nav_map = {
            "Account": [page_login],
            "AI": [page_ai_assistant],
        }

    pg = st.navigation(nav_map)
else:
    # Logged-out navigation
    pg = st.navigation(
        {
            "Account": [page_login],
            "AI": [page_ai_assistant],
        }
    )

pg.run()
