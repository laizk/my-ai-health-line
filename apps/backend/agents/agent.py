import os
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory, preload_memory
from google.adk.tools import google_search, AgentTool, ToolContext
from google.adk.tools.function_tool import FunctionTool
from agents.tools.account_tools import identify_user
from agents.tools.patient_tools import handle_patient_action
from agents.tools.carer_tools import handle_carer_action
from agents.tools.user_tools import handle_user_action


def load_instruction(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


from utils import retry_config

API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = "gemini-2.5-flash"
APP_NAME = "Base Agent"
USER_ID = "guest_user"

db_agent = LlmAgent(
    name="db_assistant",
    model=Gemini(model=LLM_MODEL, retry_options=retry_config),
    description="A helpful DB assistant",
    instruction=load_instruction(
        os.path.join(os.path.dirname(__file__), "instructions", "db_agent.txt")
    ),
    tools=[
            handle_patient_action,
            handle_carer_action,
            handle_user_action,
    ],
)

concierge_agent = LlmAgent(
    name="concierge_assistant",
    model=Gemini(model=LLM_MODEL, retry_options=retry_config),
    description="A helpful healthcare assistant.",
    instruction=load_instruction(
        os.path.join(os.path.dirname(__file__), "instructions", "concierge_agent.txt")
    ),
    tools=[
        # google_search,
        load_memory,
        preload_memory,
        identify_user,
        AgentTool(agent=db_agent),
    ],
)


print("✅ Agents created")

session_service = InMemorySessionService()  # Handles conversations
memory_service = InMemoryMemoryService()


# Create runner with BOTH services
runner = Runner(
    agent=concierge_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,
)
print("✅ Agent and Runner created with memory support!")
