from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from agent import chatbot
class chatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

app = FastAPI(title="Chatbot API", version="1.0.0", description="A simple chatbot API using FastAPI and Litellm.")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/chat")
def send_message(request: chatRequest):
    response, session_id = chatbot(
        message=request.message,
        session_id=request.session_id
    ) 
    return { "session_id": session_id, "response": response }


@app.get("/health")
def health_check():
    return {"status": "healthy"}