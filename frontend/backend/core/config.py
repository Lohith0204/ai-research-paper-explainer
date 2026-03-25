import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Research Paper Explainer"

    # API Keys
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")

    # Vector settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 5

    # Deployment
    PORT: int = int(os.environ.get("PORT", 8000))
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
