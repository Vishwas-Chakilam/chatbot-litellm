import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve the path to the app/.env file
# Path(__file__).resolve() is app/core/config.py
# parent is app/core/
# parent.parent is app/
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

def get_env_var(key: str, default: str = None) -> str:
    """Helper to retrieve environment variables."""
    return os.getenv(key, default)
