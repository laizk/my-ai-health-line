import streamlit as st
from uuid import uuid4


@st.cache_resource
def _token_store():
    """In-memory token store shared across sessions (lives inside the Streamlit process)."""
    return {}


def hydrate_auth_from_params():
    """Populate session auth from query params + token store if available."""
    if "auth" in st.session_state:
        return st.session_state["auth"]

    token = st.query_params.get("token")
    if isinstance(token, list):
        token = token[0] if token else None

    if not token:
        return None

    auth_payload = _token_store().get(token)
    if auth_payload:
        st.session_state["auth"] = auth_payload
        st.session_state["auth_token"] = token
        return auth_payload

    return None


def persist_auth(auth_payload):
    """Persist auth to session state, token store, and query params."""
    token = str(uuid4())
    _token_store()[token] = auth_payload
    st.session_state["auth"] = auth_payload
    st.session_state["auth_token"] = token
    st.query_params.update({"token": token})
    return token


def clear_auth():
    """Clear auth from session and query params."""
    st.session_state.pop("auth", None)
    token = st.session_state.pop("auth_token", None)
    st.query_params.clear()
    return token
