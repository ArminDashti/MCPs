import os
import datetime

# Configuration for the LLM application

# API Token for Openrouter (or other LLM provider)
TOKEN = "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"  # Replace with your actual API token

# Default LLM model to use
MODEL = "kwaipilot/kat-coder-pro:free" # Example model, change as needed

# Function to generate dynamic log directory and file path
def get_log_filepath():
    user_folder = os.path.expanduser("~") # Gets the user's home directory
    log_base_dir = os.path.join(user_folder, "h2o")
        
    current_date = datetime.datetime.now().strftime("%y-%m-%d")
    current_time = datetime.datetime.now().strftime("%H%M")
    
    log_dir = os.path.join(log_base_dir, current_date)
    os.makedirs(log_dir, exist_ok=True) # Ensure the directory exists
    
    log_filename = f"{current_time}.txt"
    return os.path.join(log_dir, log_filename)

# Example usage (for demonstration, not part of actual config)
# log_filepath = get_log_filepath()
# print(f"Log file will be saved to: {log_filepath}")

# Format of each log entry
LOG_ENTRY_FORMAT = """Model: {model_name}

User prompt:
{user_prompt}

LLM response: (from Openrouter)
{llm_response}

=================================="""

