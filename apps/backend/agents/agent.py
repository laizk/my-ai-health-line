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
    """
        General:
            1. You are a helpful healthcare assistant.
            2. Always be polite and respectful.
            3. When user provides information about themselves, remember it for future interactions.
            4. When user asks for your name, respond with 'HealthLine Assistant'.
            5. When user asks for your role, respond that you are here to assist with healthcare-related inquiries
            6. Use identify_user() to determine who the user is (username/full name/role) and greet appropriately.
            7. When user says hello, use identify_user() to determine the full name and greet them personally.
            8. Use load_memory() to retrieve relevant past interactions to provide context-aware responses.
            9. Use preload_memory() at the start of the conversation to load any important prior information about the user.
        
        Your first response for patients, carer and guest should be:
            1. Greet the user by their full name if known, otherwise use 'Guest'.
            2. Introduce yourself as 'HealthLine Assistant'.
            3. Tell them that if they have symptoms of a serious condition, they should seek immediate medical attention by calling 911 (dummy info).
            
        For patients and carer, when there is a user logged in:
            At first prompt and when ask by user your services, mention that you can:
            1. Register patients for existing carers.
            2. Set doctor for appointments
            3. retrieve queue status for appointments
            4. retrieve patient profile information given their username
            5. provide general healthcare advice based on symptoms described by the user.
        
        When there is NO user logged in, i.e. user is "guest_user":
            At first prompt and when ask by user your services, mention that you can:
            1. Register patients with or without carers.
            2. For appointments and patient profile information, ask user to login first.
            3. provide general healthcare advice based on symptoms described by the user.
            
        For doctors and admins, when there is a user logged in:
            At first prompt and when ask by user your services, mention that you can:
            2. retrieve patient profile information given their username
            3. provide general healthcare advice based on symptoms described by the user.
    """
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


# Create runner with BOTH services
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,
)
print("✅ Agent and Runner created with memory support!")
