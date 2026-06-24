import os
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv
from litellm import completion
from prompts import CHATBOT_SYSTEM_PROMPT, ROUTER_SYSTEM_PROMPT

load_dotenv()

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)


# -----------------------------
# Session Helpers
# -----------------------------
def get_session_file(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"


def load_history(session_id: str) -> list:
    session_file = get_session_file(session_id)

    if session_file.exists():
        with open(session_file, "r", encoding="utf-8") as f:
            return json.load(f)

    return []


def save_history(session_id: str, history: list):
    session_file = get_session_file(session_id)

    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


# -----------------------------
# Layer 1 : Static Responses
# -----------------------------
def static_response(message: str):
    msg = message.lower().strip()

    static_responses = {
        "hello": "Hello! How can I assist you today?",
        "hi": "Hi there! What can I do for you?",
        "how are you": "I'm just a bot, but I'm here to help!",
        "what's your name": "I'm a chatbot created to assist you.",
        "help": "Sure! Ask me anything.",
        "thank you": "You're welcome!",
        "good morning": "Good morning!",
        "good afternoon": "Good afternoon!",
        "good evening": "Good evening!",
        "good night": "Good night!",
        "hey": "Hey there!",
        "see you": "Have a great day!",
        "bye": "Goodbye! Have a great day!"
    }

    return static_responses.get(msg)


# -----------------------------
# Layer 2 : Rule-based Router
# -----------------------------
def classify_by_rules(message: str) -> str:
    msg = message.lower().strip()

    complex_keywords = [
        "analyze",
        "compare",
        "design",
        "architecture",
        "optimize",
        "debug",
        "medical",
        "finance",
        "algorithm",
        "system"
    ]

    if len(msg) > 500:
        return "complex"

    if any(word in msg for word in complex_keywords):
        return "complex"

    if len(msg) < 50:
        return "simple"

    return "uncertain"


# -----------------------------
# Layer 3 : LLM Router
# -----------------------------
def llm_router(message: str) -> str:
    response = completion(
        model=os.getenv("FAST_MODEL_1"),
        api_key=os.getenv("FAST_API_KEY_1"),
        messages=[
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
    )

    decision = response.choices[0].message.content.strip().upper()
    return decision


# -----------------------------
# Model Selection
# -----------------------------
def choose_model(message: str):
    rule_result = classify_by_rules(message)

    if rule_result == "simple":
        return (
            os.getenv("FAST_MODEL_1"),
            os.getenv("FAST_API_KEY_1")
        )

    if rule_result == "complex":
        return (
            os.getenv("CAPABLE_MODEL_1"),
            os.getenv("CAPABLE_API_KEY_1")
        )

    decision = llm_router(message)

    if decision == "CAPABLE":
        return (
            os.getenv("CAPABLE_MODEL_1"),
            os.getenv("CAPABLE_API_KEY_1")
        )

    return (
        os.getenv("FAST_MODEL_1"),
        os.getenv("FAST_API_KEY_1")
    )


# -----------------------------
# Main Chatbot Function
# -----------------------------
def chatbot(message: str, session_id=None):
    if session_id is None:
        session_id = str(uuid.uuid4())[:8]

    history = load_history(session_id)

    # Layer 1
    reply = static_response(message)
    if reply:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})
        save_history(session_id, history)
        return reply, session_id

    model, api_key = choose_model(message)

    if not model or not api_key:
        raise ValueError("Model or API key missing in environment")

    history.append({"role": "user", "content": message})

    try:
        messages = [
            {"role": "system", "content": CHATBOT_SYSTEM_PROMPT}
        ] + history

        response = completion(
            model=model,
            api_key=api_key,
            messages=messages,
            max_tokens=300
        )

        answer = response.choices[0].message.content.strip()

        history.append({
            "role": "assistant",
            "content": answer
        })

        save_history(session_id, history)

        return answer, session_id

    except Exception as e:
        print(f"Error occurred: {e}")
        return "Sorry, I couldn't process your request.", session_id