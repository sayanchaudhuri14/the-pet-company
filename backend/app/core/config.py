from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Required — no default. App refuses to start if not set in environment or .env file.
    # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 min; was 24h — reduces stolen-token window

    # Database — defaults to local SQLite for development
    DATABASE_URL: str = "sqlite:///./petcompany.db"

    # CORS — override in production with your actual frontend domain(s)
    # Example: ALLOWED_ORIGINS=["https://thepetcompany.com"]
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5500", "http://127.0.0.1:5500"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
