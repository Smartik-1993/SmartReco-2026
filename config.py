import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartReco"
    DATABASE_URL: str = "sqlite:///./smartreco.db"
    MESH_API_KEY: str = "mock_mesh_api_key"
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str = "mock_langsmith_api_key"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()