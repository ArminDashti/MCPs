import os
import json
from datetime import datetime
from typing import Optional


class DailyLogger:
    def __init__(self, log_dir: Optional[str]):
        self.log_dir = log_dir
        if self.log_dir:
            self._ensure_log_dir()

    def _ensure_log_dir(self) -> None:
        if self.log_dir and not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    def _get_log_file_path(self) -> str:
        # Format: 25_11_05_14_15_32.txt (YY_MM_DD_HH_MM_SS.txt)
        filename = datetime.now().strftime("%y_%m_%d_%H_%M_%S.txt")
        return os.path.join(self.log_dir, filename)

    def log_prompt(self, 
                   prompt: str, 
                   response: Optional[str] = None, 
                   model: Optional[str] = None,
                   response_time: Optional[float] = None,
                   error: Optional[str] = None) -> None:
        """
        Log prompt and response with the specified format.
        If log_dir is None, logging is disabled (no-op).
        """
        # Skip logging if no directory is configured
        if not self.log_dir:
            return
        
        log_file = self._get_log_file_path()
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Format response time if provided
        response_time_str = f"{response_time:.3f}s" if response_time is not None else "N/A"
        
        # Format model if provided
        model_str = model if model else "N/A"
        
        # Build log entry
        log_entry = f"Date: {date_str}\n"
        log_entry += f"Time: {time_str}\n"
        log_entry += f"Model: {model_str}\n"
        log_entry += f"Response time: {response_time_str}\n\n"
        log_entry += f"prompt:\n{prompt}\n\n"
        
        if error:
            log_entry += f"response:\n[Error: {error}]\n"
        elif response:
            log_entry += f"response:\n{response}\n"
        else:
            log_entry += "response:\n[N/A]\n"
        
        log_entry += "\n" + "=" * 80 + "\n\n"

        try:
            # Append to log file (not overwrite)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Failed to log prompt: {e}")

