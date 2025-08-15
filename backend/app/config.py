# app/config.py
import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Manages application configuration using environment variables."""
    DASHSCOPE_API_KEY: str = Field(..., env="DASHSCOPE_API_KEY")
    DOUBAO_API_KEY: str = Field(..., env="DOUBAO_API_KEY")
    DEFAULT_MODEL: str = Field("deepseek-v3-250324", env="DEFAULT_MODEL") #Moonshot-Kimi-K2-Instruct
    DEFAULT_VISION_MODEL: str = Field("doubao-1-5-thinking-vision-pro-250428", env="DEFAULT_VISION_MODEL")
    MAX_RETRIES: int = Field(3, env="MAX_RETRIES")
    
    # Define a directory for temporary files
    TEMP_DIR: str = "temp_data"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

# Ensure the temporary directory exists
os.makedirs(settings.TEMP_DIR, exist_ok=True)