from pathlib import Path
from typing import TypeVar

import yaml
from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseModel, Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsError(ValueError):
    """Raised when required environment settings are missing or invalid."""


class ConfigurationError(ValueError):
    """Raised when declarative YAML cannot be loaded or validated."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    proxy_url: AnyHttpUrl = Field(validation_alias="LITELLM_PROXY_URL")
    proxy_api_key: SecretStr = Field(validation_alias="LITELLM_PROXY_API_KEY")
    model_name: str = Field(min_length=1, validation_alias="MODEL_NAME")


_SETTING_ENV_NAMES = {
    "proxy_url": "LITELLM_PROXY_URL",
    "proxy_api_key": "LITELLM_PROXY_API_KEY",
    "model_name": "MODEL_NAME",
}


def load_settings(env_file: str | Path | None = None) -> Settings:
    """Load and validate settings, optionally reading a dotenv file."""
    load_dotenv(dotenv_path=env_file, override=False)
    try:
        return Settings()
    except ValidationError as error:
        invalid_fields = sorted(
            {
                _SETTING_ENV_NAMES.get(str(item["loc"][0]), str(item["loc"][0]))
                for item in error.errors(include_input=False)
            }
        )
        field_list = ", ".join(invalid_fields)
        raise SettingsError(
            f"Invalid settings; check required values: {field_list}."
        ) from None


ConfigT = TypeVar("ConfigT", bound=BaseModel)


def load_yaml_config(path: str | Path, model_type: type[ConfigT]) -> ConfigT:
    """Safely parse a YAML file and validate it with a Pydantic model."""
    config_path = Path(path)
    try:
        parsed = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConfigurationError(
            f"Could not read YAML configuration: {config_path}"
        ) from error
    except yaml.YAMLError:
        raise ConfigurationError(
            f"Malformed YAML in configuration: {config_path}"
        ) from None

    try:
        return model_type.model_validate(parsed)
    except ValidationError as error:
        invalid_fields = sorted(
            ".".join(str(part) for part in item["loc"])
            for item in error.errors(include_input=False)
        )
        field_list = ", ".join(invalid_fields)
        raise ConfigurationError(
            f"Configuration schema validation failed for {config_path} ({field_list})."
        ) from None
