from .intent_router import classify_by_rules, llm_router
from ..core.config import get_env_var

def choose_model(message: str) -> tuple[str, str]:
    """
    Selects the appropriate LLM model and API Key based on rules and LLM classification.
    Returns: (model_name, api_key)
    """
    rule_result = classify_by_rules(message)

    if rule_result == "simple":
        return (
            get_env_var("FAST_MODEL_1"),
            get_env_var("FAST_API_KEY_1")
        )

    if rule_result == "complex":
        return (
            get_env_var("CAPABLE_MODEL_1"),
            get_env_var("CAPABLE_API_KEY_1")
        )

    decision = llm_router(message)

    if decision == "CAPABLE":
        return (
            get_env_var("CAPABLE_MODEL_1"),
            get_env_var("CAPABLE_API_KEY_1")
        )

    return (
        get_env_var("FAST_MODEL_1"),
        get_env_var("FAST_API_KEY_1")
    )
