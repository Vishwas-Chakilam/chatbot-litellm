import os # for getting environment variables
import json #creating json and fetch them
import uuid #creating session id 
from pathlib import Path
from dotenv import load_dotenv
from litellm import completion
load_dotenv()
SESSIONS_DIR=Path('sessions')
SESSIONS_DIR.mkdir(exist_ok=True)

def  get_session_file(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"

def load_history(session_id: str) -> list:
    session_file = get_session_file(session_id)
    if session_file.exists():
        with open(session_file, 'r') as f:
            return json.load(f)
    return []

def save_history(session_id: str, history: list):
    session_file = get_session_file(session_id)
    with open(session_file, 'w') as f:
        json.dump(history, f)

def  static_response(message: str) -> str:
    msg=message.lower().strip()
    static_responses = {
        "hello": "Hello! How can I assist you today?",
        "hi": "Hi there! What can I do for you?",
        "how are you": "I'm just a bot, but I'm here to help you!",
        "what's your name": "I'm a chatbot created to assist you.",
        "help": "Sure! You can ask me anything or tell me what you need help with.",
        "thank you": "You're welcome! If you have any more questions, feel free to ask.",
        "good morning": "Good morning! How can I assist you today?",
        "good afternoon": "Good afternoon! How can I assist you today?",
        "good evening": "Good evening! How can I assist you today?",
        "good night": "Good night! If you have any questions, feel free to ask.",
        "hey": "Hey there! How can I help you?",
        "see you": "Have a great day!",
        "bye": "Goodbye! Have a great day!"
    }
    
    return static_responses.get(message)

def is_complex(message:str)-> bool:
    msg=message.lower().strip()
    complex_keywords=[
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
    if len(msg)>500:
        return "complex"

    if any(word in msg for word in complex_keywords):
        return "complex"
    if len(msg)<50:
        return "simple"
    return "uncertain"

def classify_by_rules(message:str):
    router_prompt=f"""
    Classify this query into one category:
    FAST or CAPABLE

    FAST:
    - simple Q&A
    - greetings
    - summaries
    - casual chat

    CAPABLE:
    - coding
    - reasoning
    - debugging
    - architecture
    - analysis

    Return only one word
    Query:{message}
    """
    response=completions(
        model=os.getenv("FAST_MODEL_1"),
        api_key=os.getenv("FAST_API_KEY_1"),
        messages=[{"role":"user","content":router_prompt}]
    )
    decision=response.choices[0].message.content.strip().upper()
    return decision

def choose_model(message:str):
    rule_result=classify_by_rules(message)
    if rule_result=="simple":
        return(
            os.getenv("FAST_MODEL_1"),
            os.getenv("FAST_API_KEY_1")
        )
    if rule_result=="complex":
        return(
            os.getenv("CAPABLE_MODEL_1"),
            os.getenv("CAPABLE_API_KEY_1")
        )
    decision=llm(router)
    if decision=="CAPABLE":
        return (
            os.getenv("CAPABLE_MODEL_1"),
            os.getenv("CAPABLE_API_KEY_1")
        )
    return (
            os.getenv("FAST_MODEL_1"),
            os.getenv("FAST_API_KEY_1")
    )

def chatbot(message: str, session_id=None):
    reply=static_response(message)
    if reply:
        return reply,session_id
    
    model,apikey=choose_model(message)

    if not model or not api_key:
        raise ValueError("Model or API key not found in environment variables.")
    if session_id is None:
        session_id = str(uuid.uuid4())[:8]
    history = load_history(session_id)
    history.append({"role": "user", "content": message})
    try:
        response = completion(
            model=model,
            api_key=api_key,
            messages=history,
            max_tokens=100
        )
        answer = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": response.choices[0].message.content.strip()})
        save_history(session_id, history)
        return answer, session_id
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Sorry, I couldn't process your request at the moment."