import os
import datetime
import traceback
from typing import Optional

from ..config import Config


DIVIDER = "-" * 80


def log_prompt(
    model_name: str, 
    response_time: float, 
    original_prompt: str, 
    response: str
) -> None:
    """Log a prompt and its response for debugging and analysis."""
    today = datetime.datetime.now()
    log_dir = os.path.join(Config.PROMPT_LOG_DIR, today.strftime("%Y_%m_%d"))
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, today.strftime("%H_%M_%S") + ".txt")
    
    content = (
        f"Datetime: {today.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Model name: {model_name}\n"
        f"Response time: {response_time:.2f} seconds\n"
        f"{DIVIDER}\n"
        f"Original prompt: {original_prompt}\n"
        f"{DIVIDER}\n"
        f"Response: {response}\n"
    )
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(content)


def log_exception(exc: Exception, context: Optional[str] = None) -> None:
    """Log an exception with optional context information."""
    today = datetime.datetime.now()
    log_dir = os.path.join(Config.EXCEPTION_LOG_DIR, today.strftime("%Y_%m_%d"))
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, today.strftime("%H_%M_%S_%f") + ".txt")
    
    content = f"Exception occurred: {exc}\n"
    if context:
        content += f"Context: {context}\n"
    content += f"{DIVIDER}\n"
    content += f"Traceback:\n{traceback.format_exc()}"
    
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(content)


def get_log_stats() -> dict:
    """Get statistics about logged prompts and exceptions."""
    stats = {
        "prompt_logs": 0,
        "exception_logs": 0,
        "latest_prompt": None,
        "latest_exception": None
    }
    
    # Count prompt logs
    if os.path.exists(Config.PROMPT_LOG_DIR):
        for root, dirs, files in os.walk(Config.PROMPT_LOG_DIR):
            stats["prompt_logs"] += len([f for f in files if f.endswith(".txt")])
            if files and not stats["latest_prompt"]:
                latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(root, f)))
                stats["latest_prompt"] = os.path.join(root, latest_file)
    
    # Count exception logs
    if os.path.exists(Config.EXCEPTION_LOG_DIR):
        for root, dirs, files in os.walk(Config.EXCEPTION_LOG_DIR):
            stats["exception_logs"] += len([f for f in files if f.endswith(".txt")])
            if files and not stats["latest_exception"]:
                latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(root, f)))
                stats["latest_exception"] = os.path.join(root, latest_file)
    
    return stats
