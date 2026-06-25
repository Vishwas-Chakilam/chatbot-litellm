import uuid
from litellm import completion

# Import modular components
from .core.prompts import CHATBOT_SYSTEM_PROMPT
from .memory.session_manager import load_history, save_history
from .routers.intent_router import static_response
from .routers.model_router import choose_model
from .services.llm_service import (
    check_input_safety,
    defend_history_poisoning,
    check_output_safety
)

def chatbot(message: str, session_id: str = None) -> tuple[str, str]:
    """
    Orchestrates the chatbot request lifecycle using modular sub-services.
    Returns: (response_text, session_id)
    """
    if session_id is None:
        session_id = str(uuid.uuid4())[:8]

    history = load_history(session_id)

    # 1. Run Input Guardrail Check (L1)
    is_safe, risk_level = check_input_safety(message, history)
    if not is_safe:
        return "I cannot fulfill this request. It violates my safety guidelines.", session_id

    # 2. Check for fast static responses
    reply = static_response(message)
    if reply:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})
        save_history(session_id, history)
        return reply, session_id

    # 3. Mitigate multi-turn context poisoning (L2) ONLY if risk level is elevated (MEDIUM)
    if risk_level == "MEDIUM":
        history = defend_history_poisoning(history)

    # 4. Route model selection based on intent classification
    model, api_key = choose_model(message)
    if not model or not api_key:
        raise ValueError("Model or API key missing in environment")

    # Append current prompt to active context
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

        # 5. Run Output Guardrail Check (L3)
        if not check_output_safety(answer):
            return "I generated a response that violates my safety guidelines, so I cannot present it to you.", session_id

        # Update saved history
        history.append({
            "role": "assistant",
            "content": answer
        })
        save_history(session_id, history)

        return answer, session_id

    except Exception as e:
        print(f"Error occurred in LLM execution: {e}")
        return "Sorry, I couldn't process your request.", session_id