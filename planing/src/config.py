import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the MCP Planner."""
    
    # OpenRouter API settings
    OPENROUTER_API_KEY: str = os.getenv("openrouter_planing_key", "")
    PLANNER_MODEL: str = os.getenv("mcp_planner_model", "openai/gpt-5.2")
    
    # Logging settings
    LOG_DIR: str = os.getenv("MCP_PLANNER_LOG_DIR", os.path.expanduser("~/.mcp_planner"))
    PROMPT_LOG_DIR: str = os.path.join(LOG_DIR, "prompts")
    EXCEPTION_LOG_DIR: str = os.path.join(LOG_DIR, "logs", "exceptions")
    
    # API settings
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    REQUEST_TIMEOUT: int = 60
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is required. Set it in your .env file.")
        
        # Ensure log directories exist
        os.makedirs(cls.PROMPT_LOG_DIR, exist_ok=True)
        os.makedirs(cls.EXCEPTION_LOG_DIR, exist_ok=True)
