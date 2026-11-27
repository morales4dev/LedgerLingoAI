from openai import AsyncOpenAI

from ledgerlingo.config import Settings


def create_client(settings: Settings) -> AsyncOpenAI:
    """Create an OpenAI SDK client configured for the LiteLLM Proxy."""
    return AsyncOpenAI(
        base_url=str(settings.proxy_url),
        api_key=settings.proxy_api_key.get_secret_value(),
    )
