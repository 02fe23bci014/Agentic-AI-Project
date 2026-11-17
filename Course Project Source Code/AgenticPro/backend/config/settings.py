from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Programming Lab Auto Evaluation"
    database_path: str = "./database/evaluations.db"
    allowed_origins: list[str] = ["http://localhost:5173"]

    ollama_api_key: str = ""
    ollama_model: str = "gpt-oss:120b"
    ollama_base_url: str = "https://ollama.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()