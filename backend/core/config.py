import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Theological AI Agent"
    VERSION: str = "1.0.0"
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_MODEL_NAME: str = os.getenv("GOOGLE_MODEL_NAME", "gemini-1.5-flash")
    CHROMADB_HOST: str = os.getenv("CHROMADB_HOST", "localhost")
    CHROMADB_PORT: int = int(os.getenv("CHROMADB_PORT", 8000))
    SOURCE_DOCS_PATH: str = os.getenv("SOURCE_DOCS_PATH", "source_docs")
    
    class Config:
        env_file = ".env"

settings = Settings()
