import os
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory, preload_memory
from google.adk.tools import google_search
from agents.tools import identify_user

from utils import retry_config

# from tools import memory_read, memory_write

API_KEY = os.getenv("GOOGLE_API_KEY")
APP_NAME = "Base Agent"
USER_ID = "guest_user"

root_agent = LlmAgent(
    name="helpful_assistant",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    description="A helpful healthcare assistant.",
    instruction=(
        "You are a helpful assistant. Use Google Search for current info or if unsure. "
        "Use identify_user() to determine who the user is (username/full name/role) and greet appropriately."
        "When user says hello, use identify_user() to determine the full name and greet them personally."
    ),
    
    tools=[
        # google_search,
        identify_user,
        load_memory,
        preload_memory,
    ]
)
print("✅ Agent created")

session_service = InMemorySessionService()  # Handles conversations
memory_service =  InMemoryMemoryService()


# runner = InMemoryRunner(agent=root_agent)

# Create runner with BOTH services
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,
)
print("✅ Agent and Runner created with memory support!")
