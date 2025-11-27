import os
from fastapi import FastAPI
from pydantic import BaseModel
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types
from utils import retry_config

app = FastAPI(title="My AI Health Line Backend")

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Load API Key
API_KEY = os.getenv("GOOGLE_API_KEY")

# Create the agent
root_agent = Agent(
    name="helpful_assistant",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    description="A simple agent that can answer general questions.",
    instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
    tools=[google_search],
)

print("✅ Root Agent defined.")

runner = InMemoryRunner(agent=root_agent)

print("✅ Runner created.")


class AskRequest(BaseModel):
    prompt: str

@app.post("/ask")
async def ask_agent(req: AskRequest):
    
    response = await runner.run_debug(
        req.prompt
    )    
    return {"response": response}