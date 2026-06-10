from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    GOOGLE_API_KEY: str | None = None

    CHROMA_HOST: str = "chroma"
    CHROMA_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()