import os

from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


def get_model(
    llm_key_var: str = "LLM_API_KEY",
    llm_url_var: str = "LLM_BASE_URL",
    llm_model_var: str = "LLM_MODEL",
    llm_model: str | None = None,  # Optional override
):
    """OpenAI-compatible LLM model factory function."""
    _ = load_dotenv()
    api_key = os.getenv(llm_key_var)
    model_name = llm_model if llm_model is not None else os.getenv(llm_model_var)
    if not api_key:
        raise ValueError(f"API key not found in environment variable '{llm_key_var}'")
    if not model_name:
        raise ValueError(f"Model not found in environment variable '{llm_model_var}'")
    base_url = os.getenv(llm_url_var)
    if not base_url:
        raise ValueError(f"Base URL not found in environment variable '{llm_url_var}'")

    model = OpenAIChatModel(
        model_name,
        provider=OpenAIProvider(api_key=api_key, base_url=base_url),
    )
    return model
