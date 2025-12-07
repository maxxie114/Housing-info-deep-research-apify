import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    apify_api_url: str
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure environment variables are set for downstream SDKs
if settings.openai_api_key:
    os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
if settings.apify_api_url:
    os.environ.setdefault("APIFY_API_URL", settings.apify_api_url)
