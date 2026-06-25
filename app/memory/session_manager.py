from pathlib import Path
import json

# Ensure sessions directory is always created at the root workspace directory
SESSIONS_DIR = Path(__file__).resolve().parent.parent.parent / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

def get_session_file(session_id: str) -> Path:
    """Gets the path to the session JSON file."""
    return SESSIONS_DIR / f"{session_id}.json"

def load_history(session_id: str) -> list:
    """Loads chat history for a session from storage."""
    session_file = get_session_file(session_id)
    if session_file.exists():
        with open(session_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_history(session_id: str, history: list):
    """Saves chat history for a session to storage."""
    session_file = get_session_file(session_id)
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
