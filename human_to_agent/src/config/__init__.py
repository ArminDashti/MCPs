"""Config module for h2a project."""
import os
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from config.json
_config_path = Path(__file__).parent / "config.json"
try:
    with open(_config_path, 'r', encoding='utf-8') as f:
        _config = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"Configuration file not found: {_config_path}")
except Exception as e:
    raise ValueError(f"Error loading config.json: {e}")

# API Token for Openrouter (or other LLM provider)
# Priority: environment variable > config.json
TOKEN = os.getenv("openrouter_api_key") or _config["api"]["token"]

# Planning API Token for Openrouter (separate key for planning operations)
# Priority: environment variable > regular TOKEN > config.json
PLANNING_TOKEN = os.getenv("openrouter_api_key_planing") or TOKEN

# Default LLM model to use
MODEL = _config["api"]["model"]

# Function to get log directory path
def get_log_directory():
    """
    Returns the log directory path based on config.
    If directory is defined in config, uses that path (absolute or relative).
    Returns None if no directory is defined (logging will be disabled).
    """
    logging_config = _config.get("logging", {})
    directory = logging_config.get("directory")
    
    if directory:
        # If directory is an absolute path, use it directly
        if os.path.isabs(directory):
            log_dir = directory
        else:
            # If relative path, use it relative to user's home directory
            user_folder = os.path.expanduser("~")
            log_dir = os.path.join(user_folder, directory)
        
        # Ensure the directory exists
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    else:
        # No directory defined, logging disabled
        return None

# Function to generate dynamic log directory and file path (kept for backward compatibility)
def get_log_filepath():
    log_dir = get_log_directory()
    if not log_dir:
        return None
    
    current_date = datetime.datetime.now().strftime(_config["logging"].get("date_format", "%y-%m-%d"))
    current_time = datetime.datetime.now().strftime(_config["logging"].get("time_format", "%H%M"))
    
    date_dir = os.path.join(log_dir, current_date)
    os.makedirs(date_dir, exist_ok=True)
    
    log_filename = f"{current_time}{_config['logging'].get('file_extension', '.txt')}"
    return os.path.join(date_dir, log_filename)

# Format of each log entry
LOG_ENTRY_FORMAT = _config["logging"].get("entry_format", "Model: {model_name}\n\nUser prompt:\n{user_prompt}\n\nLLM response: (from Openrouter)\n{llm_response}\n\n==================================")

__all__ = [
    'TOKEN',
    'PLANNING_TOKEN',
    'MODEL',
    'get_log_directory',
    'get_log_filepath',
    'LOG_ENTRY_FORMAT'
]
