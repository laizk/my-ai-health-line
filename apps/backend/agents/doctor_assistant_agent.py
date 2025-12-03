import os
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory, preload_memory
from google.adk.tools import google_search, AgentTool, ToolContext
from agents.tools.account_tools import identify_user
from agents.db_agent import db_agent
from agents.utils import load_instruction, retry_config



API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = "gemini-2.5-flash"
APP_NAME = "Doctor Assistant Agent"


doctor_assistant_agent = LlmAgent(
    name="doctor_assistant",
    model=Gemini(model=LLM_MODEL, retry_options=retry_config),
    description="Assistant for doctors only.",
    instruction=load_instruction(
        os.path.join(
            os.path.dirname(__file__), "instructions", "doctor_assistant_agent.txt"
        )
    ),
    tools=[
        load_memory,
        preload_memory,
        identify_user,
        AgentTool(agent=db_agent),
    ],
)


print("✅ Doctor Assistant Agents created")

session_service = InMemorySessionService()  # Handles conversations
memory_service = InMemoryMemoryService()


# Create runner with BOTH services
runner = Runner(
    agent=doctor_assistant_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,
)
print("✅ Agent and Runner created with memory support!")
