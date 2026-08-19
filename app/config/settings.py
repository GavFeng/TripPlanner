import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Multi-Agent Travel Planner API"
    DEBUG: bool = True

    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # MongoDB Atlas Configuration
    # REMEMBER TO DO THIS pip install dnspython
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    DB_NAME: str = os.getenv("DB_NAME", "travel_planner_db")
    

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()