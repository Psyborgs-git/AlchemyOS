"""Configuration module using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "alchemyos"
    postgres_user: str = "alchemyos"
    postgres_password: str = "changeme"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM Runtime
    llm_provider: str = "ollama"  # ollama | vllm | openai_shim
    llm_base_url: str = "http://localhost:11434"
    llm_model: str = "mistral:7b-instruct"
    llm_api_key: str = "not-needed"

    # Hardware
    hardware_profile: str = "cpu"  # cpu | gpu | multi-gpu

    # Safety
    safety_mode: str = "warn"  # warn | quarantine | block
    safety_admin_email: str = ""

    # Federation
    federation_enabled: bool = False
    federation_node_id: str = ""

    # MLflow
    mlflow_tracking_uri: str = "./mlruns"

    # App
    app_env: str = "development"
    secret_key: str = "changeme-generate-with-openssl-rand-hex-32"
    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        """Construct database URL from components."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


# Global settings instance
settings = Settings()
