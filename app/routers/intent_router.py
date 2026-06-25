import os
from litellm import completion
from ..core.prompts import ROUTER_SYSTEM_PROMPT
from ..core.config import get_env_var

def static_response(message: str) -> str:
    """Provides fast static replies for generic greetings or goodbye phrases."""
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

def classify_by_rules(message: str) -> str:
    """Pre-classifies messages by size and keywords before sending to LLM router."""
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

def llm_router(message: str) -> str:
    """Utilizes a fast LLM to categorize query complexity."""
    model = get_env_var("FAST_MODEL_1")
    api_key = get_env_var("FAST_API_KEY_1")

    response = completion(
        model=model,
        api_key=api_key,
        messages=[
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
    )

    decision = response.choices[0].message.content.strip().upper()
    return decision
