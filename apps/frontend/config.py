import os

# Base backend URL assembled from env vars for flexibility
BACKEND_HOST = os.getenv("BACKEND_HOST", "backend")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8010")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", f"http://{BACKEND_HOST}:{BACKEND_PORT}")

# Service endpoints
PATIENTS_API = f"{BACKEND_BASE_URL}/patients"
AUTH_LOGIN_API = f"{BACKEND_BASE_URL}/auth/login"
ASK_API = f"{BACKEND_BASE_URL}/ask"
ASK_HISTORY_API = f"{BACKEND_BASE_URL}/ask/history"
ASK_HISTORY_BY_USER_API = f"{BACKEND_BASE_URL}/ask/history/by_user"
