import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    HUGGINGFACE_TOKEN: Optional[str] = os.getenv("HUGGINGFACE_TOKEN")
    
    # Database
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    
    # Models
    ROUTER_MODEL: str = "gpt-3.5-turbo"
    GENERATOR_MODEL: str = "gpt-4o-mini"  # Cheaper than gpt-4
    
    # Usage tracking
    TRACK_USAGE: bool = os.getenv("TRACK_USAGE", "false").lower() == "true"
    
    # System settings
    MAX_CONTEXT_LENGTH: int = 2000
    MAX_PROBLEMS_KB: int = 1500
    
    @classmethod
    def validate_required_keys(cls):
        """Validate that required API keys are present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required in .env file")
        
        if not cls.OPENAI_API_KEY.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format")
        
        return True

settings = Settings()