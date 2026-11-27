from pathlib import Path

import pytest
from pydantic import BaseModel

from ledgerlingo.config import (
    ConfigurationError,
    SettingsError,
    load_settings,
    load_yaml_config,
)


def test_load_settings_from_dotenv_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "LITELLM_PROXY_URL=http://localhost:4000/v1\n"
        "LITELLM_PROXY_API_KEY=proxy-secret\n"
        "MODEL_NAME=local-model\n",
        encoding="utf-8",
    )
    for key in ("LITELLM_PROXY_URL", "LITELLM_PROXY_API_KEY", "MODEL_NAME"):
        monkeypatch.delenv(key, raising=False)

    settings = load_settings(env_file)

    assert str(settings.proxy_url) == "http://localhost:4000/v1"
    assert settings.proxy_api_key.get_secret_value() == "proxy-secret"
    assert settings.model_name == "local-model"


def test_load_settings_reports_missing_required_values_safely(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")
    for key in ("LITELLM_PROXY_URL", "LITELLM_PROXY_API_KEY", "MODEL_NAME"):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(SettingsError) as error:
        load_settings(env_file)

    assert "LITELLM_PROXY_URL" in str(error.value)
    assert "LITELLM_PROXY_API_KEY" in str(error.value)
    assert "MODEL_NAME" in str(error.value)
    assert "input_value" not in str(error.value)


def test_load_settings_does_not_expose_secret_on_validation_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "LITELLM_PROXY_URL=not-a-url\n"
        "LITELLM_PROXY_API_KEY=must-not-leak\n"
        "MODEL_NAME=local-model\n",
        encoding="utf-8",
    )
    for key in ("LITELLM_PROXY_URL", "LITELLM_PROXY_API_KEY", "MODEL_NAME"):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(SettingsError) as error:
        load_settings(env_file)

    assert "LITELLM_PROXY_URL" in str(error.value)
    assert "must-not-leak" not in str(error.value)


class ExampleYamlConfig(BaseModel):
    enabled: bool


def test_load_yaml_config_validates_model(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("enabled: true\n", encoding="utf-8")

    config = load_yaml_config(config_path, ExampleYamlConfig)

    assert config == ExampleYamlConfig(enabled=True)


def test_load_yaml_config_rejects_malformed_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("enabled: [true\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Malformed YAML"):
        load_yaml_config(config_path, ExampleYamlConfig)


def test_load_yaml_config_rejects_schema_invalid_data(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("enabled: maybe\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="enabled"):
        load_yaml_config(config_path, ExampleYamlConfig)
