from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Insurance Policy & Claim Management System"
    app_version: str = "1.0.0"

    database_url: str = "sqlite:///./insurance.db"

    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"

    access_token_expire_minutes: int = 300
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()