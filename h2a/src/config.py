import os
import json
from pathlib import Path
import datetime

# Configuration for the LLM application embedded directly
_config = {
  "api": {
    "token": "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",
    "model": "kwaipilot/kat-coder-pro:free"
  },
  "logging": {
    "base_directory": "h2o",
    "date_format": "%y-%m-%d",
    "time_format": "%H%M",
    "file_extension": ".txt",
    "entry_format": "Model: {model_name}\n\nUser prompt:\n{user_prompt}\n\nLLM response: (from Openrouter)\n{llm_response}\n\n=================================="
  }
}

# API Token for Openrouter (or other LLM provider)
TOKEN = _config["api"]["token"]

# Default LLM model to use
MODEL = _config["api"]["model"]

# Function to generate dynamic log directory and file path
def get_log_filepath():
    user_folder = os.path.expanduser("~") # Gets the user's home directory
    log_base_dir = os.path.join(user_folder, _config["logging"]["base_directory"])

    current_date = datetime.datetime.now().strftime(_config["logging"]["date_format"])
    current_time = datetime.datetime.now().strftime(_config["logging"]["time_format"])

    log_dir = os.path.join(log_base_dir, current_date)
    os.makedirs(log_dir, exist_ok=True) # Ensure the directory exists

    log_filename = f"{current_time}{_config['logging']['file_extension']}"
    return os.path.join(log_dir, log_filename)

# Format of each log entry
LOG_ENTRY_FORMAT = _config["logging"]["entry_format"]

