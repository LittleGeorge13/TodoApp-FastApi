from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Your secret key (required, will raise error if missing)
    SECRET_KEY: str
    
    # Optional with defaults
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",          # for local development
        env_file_encoding="utf-8",
        extra="ignore"           # ignore extra env vars
    )

# Singleton instance
settings = Settings()