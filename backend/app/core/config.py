from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://docuser:docpass@localhost:5432/doceditor"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://docuser:docpass@localhost:5432/doceditor"
    SECRET_KEY: str = "dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
