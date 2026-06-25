from fastapi import FastAPI
from .core.models import chatRequest
from .memory.session_manager import SESSIONS_DIR, load_history
from .agent import chatbot

app = FastAPI(title="Chatbot API", version="2.0.0", description="A simple chatbot API using FastAPI and Litellm.")

@app.get("/", tags=["General"])
def read_root():
    return {"Hello": "World"}

@app.post("/chat", tags=["Chat"])
def send_message(request: chatRequest):
    response, session_id = chatbot(
        message=request.message,
        session_id=request.session_id
    ) 
    return {"session_id": session_id, "response": response}

@app.get("/health", tags=["General"])
def health_check():
    return {"status": "healthy"}

@app.get("/sessions", tags=["Admin"])
def view_sessions():
    files = list(SESSIONS_DIR.glob("*.json"))
    session_data = [file.name for file in files]
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

@app.get("/cost", tags=["Admin"])
def get_totalcostofallqueries():
    return {"this is yet to implement soon!": "LITELLM CHATBOT"}

@app.get("/getjson/{session_id}", tags=["Admin"])
def get_session_json(session_id: str):
    history = load_history(session_id)
    if not history:
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            return {"error": "Session not found"}
    return {"session_id": session_id, "history": history}
