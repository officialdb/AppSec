from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    APP_NAME: str = "vulnerable-api"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/secure_api_lab"

    # INTENTIONAL VULNERABILITY: Weak, static JWT secret.
    # A secure implementation would use a long, random secret
    # rotated regularly and never committed to source control.
    JWT_SECRET: str = "development-secret"
    JWT_ALGORITHM: str = "HS256"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

