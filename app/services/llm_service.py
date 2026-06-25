import os
from litellm import completion
from ..core.prompts import GUARDRAIL_SYSTEM_PROMPT, OUTPUT_GUARDRAIL_SYSTEM_PROMPT
from ..core.config import get_env_var

def check_input_safety(message: str, history: list) -> bool:
    """
    Input Guardrail (L1): Checks the user message (with recent context) for safety violations.
    Returns True if SAFE, False if UNSAFE.
    """
    model = get_env_var("FAST_MODEL_1")
    api_key = get_env_var("FAST_API_KEY_1")
    if not model or not api_key:
        return True

    # Build a context snippet from the last 2 assistant-user turns to check for Crescendo drift
    recent_context = []
    for turn in history[-4:]:
        recent_context.append(f"{turn['role'].upper()}: {turn['content']}")
    recent_context_str = "\n".join(recent_context)

    eval_message = f"Conversation History:\n{recent_context_str}\n\nLatest User Input: {message}"

    try:
        response = completion(
            model=model,
            api_key=api_key,
            messages=[
                {"role": "system", "content": GUARDRAIL_SYSTEM_PROMPT},
                {"role": "user", "content": eval_message}
            ],
            max_tokens=10,
            temperature=0.0
        )
        decision = response.choices[0].message.content.strip().upper()
        if "UNSAFE" in decision:
            return False
    except Exception as e:
        print(f"Input safety validation bypassed due to error: {e}")
        return True
    return True

def defend_history_poisoning(history: list) -> list:
    """
    History Truncation (L2): Cuts history depth to prevent adversarial build-up.
    If history has more than 6 messages (3 turns), we only retain the most recent 2 turns (4 messages).
    """
    if len(history) > 6:
        return history[-4:]
    return history

def check_output_safety(output_text: str) -> bool:
    """
    Output Guardrail (L3): Inspects the generated output before returning it.
    Returns True if SAFE, False if UNSAFE.
    """
    model = get_env_var("FAST_MODEL_1")
    api_key = get_env_var("FAST_API_KEY_1")
    if not model or not api_key:
        return True

    try:
        response = completion(
            model=model,
            api_key=api_key,
            messages=[
                {"role": "system", "content": OUTPUT_GUARDRAIL_SYSTEM_PROMPT},
                {"role": "user", "content": output_text}
            ],
            max_tokens=10,
            temperature=0.0
        )
        decision = response.choices[0].message.content.strip().upper()
        if "UNSAFE" in decision:
            return False
    except Exception as e:
        print(f"Output safety validation bypassed due to error: {e}")
        return True
    return True
