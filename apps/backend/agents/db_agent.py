import os
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool

from agents.tools.patient_tools import handle_patient_action
from agents.tools.carer_tools import handle_carer_action
from agents.tools.user_tools import handle_user_action
from agents.tools.condition_tools import handle_condition_action
from agents.tools.medication_tools import handle_medication_action
from agents.utils import load_instruction, retry_config

LLM_MODEL = "gemini-2.5-flash"

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
            handle_condition_action,
            handle_medication_action,
    ],
)

print("✅ DB Agents created")
