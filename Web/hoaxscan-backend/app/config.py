from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "HoaxScan API"
    database_url: str = ""
    cors_origins: str = "http://localhost:5173"
    jwt_secret: str = ""
    gemini_api_key: str = ""
    stub_delay_seconds: int = 0


settings = Settings()
