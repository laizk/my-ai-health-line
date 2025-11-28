from fastapi import APIRouter
from pydantic import BaseModel
from agents.agent import runner

router = APIRouter()

class AskRequest(BaseModel):
    prompt: str

@router.post("/ask")
async def ask_agent(req: AskRequest):
    response = await runner.run_debug(req.prompt)
    return {"response": response}
