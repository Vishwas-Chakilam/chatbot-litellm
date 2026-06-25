from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from .agent import chatbot , SESSIONS_DIR
from pathlib import Path

SESSIONS_DIR = Path("sessions")

class chatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

app = FastAPI(title="Chatbot API", version="1.0.0", description="A simple chatbot API using FastAPI and Litellm.")

@app.get("/", tags=["General"])
def read_root():
    return {"Hello": "World"}

@app.post("/chat",  tags=["Chat"])
def send_message(request: chatRequest):
    response, session_id = chatbot(
        message=request.message,
        session_id=request.session_id
    ) 
    return { "session_id": session_id, "response": response }


@app.get("/health", tags=["General"])
def health_check():
    return {"status": "healthy"}

@app.get("/sessions", tags=["Admin"])
def view_sessions():
    files = list(SESSIONS_DIR.glob("*.json"))

    session_data = []

    for file in files:
        session_data.append(file.name)

    return {
        "total_sessions": len(session_data),
        "sessions": session_data
    }

@app.delete("/removejson", tags=["Admin"])
def remove_json():
    deleted = []

    for file in SESSIONS_DIR.glob("*.json"):
        file.unlink()
        deleted.append(file.name)

    return {
        "deleted_count": len(deleted),
        "deleted_files": deleted
    }

@app.delete("/session/{session_id}", tags=["Admin"])
def delete_session(session_id: str):
    session_file = SESSIONS_DIR / f"{session_id}.json"

    if not session_file.exists():
        return {"error": "Session not found"}

    session_file.unlink()

    return {"message": f"{session_id} deleted"}