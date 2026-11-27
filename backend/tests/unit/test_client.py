from unittest.mock import patch

from ledgerlingo.client import create_client
from ledgerlingo.config import Settings


def test_create_client_uses_proxy_endpoint_and_credential() -> None:
    settings = Settings(
        proxy_url="http://localhost:4000/v1",
        proxy_api_key="local-proxy-key",
        model_name="ledgerlingo-local",
    )

    with patch("ledgerlingo.client.AsyncOpenAI") as openai_client:
        client = create_client(settings)

    openai_client.assert_called_once_with(
        base_url="http://localhost:4000/v1",
        api_key="local-proxy-key",
    )
    assert client is openai_client.return_value
