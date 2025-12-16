import os
import json
from datetime import datetime
from .error_logger import log_error


class DailyLogger:
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        self._ensure_log_dir()

    def _ensure_log_dir(self) -> None:
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    def _get_log_file_path(self) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"evaluations_{today}.txt")

    def log_evaluation(self, objective: str, result: str, evaluation: dict = None, error: str = None) -> None:
        log_file = self._get_log_file_path()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = {
            "timestamp": timestamp,
            "objective": objective,
            "result": result,
            "evaluation": evaluation,
            "error": error
        }

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + "\n")
                f.write("-" * 80 + "\n")
        except Exception as e:
            print(f"Warning: Failed to log evaluation: {e}")
            log_error(e, filename="logger.py", line_number=35)
