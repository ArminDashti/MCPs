import os
import sqlite3
import traceback
from datetime import datetime
from typing import Optional


class ErrorLogger:
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the error logger with SQLite database.
        
        Args:
            db_path: Path to SQLite database file. If None, uses 'errors.db' in the project root.
        """
        if db_path is None:
            # Default to project root/errors.db
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, "errors.db")
        
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Create the database and table if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    datetime TEXT NOT NULL
                )
            """)
            
            conn.commit()
            conn.close()
        except Exception as e:
            # Fallback to print if database operations fail
            print(f"Critical: Failed to initialize error database: {e}")
    
    def _extract_error_context(self, exception: Exception) -> tuple[str, int]:
        """
        Extract filename and line number from the exception traceback.
        
        Returns:
            Tuple of (filename, line_number)
        """
        try:
            tb = traceback.extract_tb(exception.__traceback__)
            if tb:
                # Get the last frame (where the error actually occurred)
                frame = tb[-1]
                filename = os.path.basename(frame.filename)
                line_number = frame.lineno
                return filename, line_number
            else:
                # Fallback if no traceback
                return "unknown", 0
        except Exception:
            return "unknown", 0
    
    def log_error(self, error: Exception, filename: Optional[str] = None, line_number: Optional[int] = None) -> None:
        """
        Log an error to the SQLite database.
        
        Args:
            error: The exception object or error message
            filename: Optional filename override. If None, extracted from traceback
            line_number: Optional line number override. If None, extracted from traceback
        """
        try:
            # Extract error message
            if isinstance(error, Exception):
                error_message = str(error)
                # Extract filename and line number from traceback if not provided
                if filename is None or line_number is None:
                    extracted_filename, extracted_line_number = self._extract_error_context(error)
                    filename = filename or extracted_filename
                    line_number = line_number or extracted_line_number
            else:
                error_message = str(error)
                if filename is None:
                    filename = "unknown"
                if line_number is None:
                    line_number = 0
            
            # Get current datetime
            error_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert into database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO errors (error, filename, line_number, datetime)
                VALUES (?, ?, ?, ?)
            """, (error_message, filename, line_number, error_datetime))
            
            conn.commit()
            conn.close()
        except Exception as e:
            # Fallback to print if logging fails (to avoid infinite loops)
            print(f"Warning: Failed to log error to database: {e}")
            print(f"Original error: {error}")
    
    def log_error_message(self, error_message: str, filename: Optional[str] = None, line_number: Optional[int] = None) -> None:
        """
        Log an error message directly (when you don't have an exception object).
        
        Args:
            error_message: The error message string
            filename: Optional filename. If None, tries to extract from current stack
            line_number: Optional line number. If None, tries to extract from current stack
        """
        try:
            # Try to extract filename and line number from current stack
            if filename is None or line_number is None:
                try:
                    stack = traceback.extract_stack()
                    if len(stack) >= 2:
                        # Get the caller's frame (skip this function)
                        frame = stack[-2]
                        extracted_filename = os.path.basename(frame.filename)
                        extracted_line_number = frame.lineno
                        filename = filename or extracted_filename
                        line_number = line_number or extracted_line_number
                    else:
                        filename = filename or "unknown"
                        line_number = line_number or 0
                except Exception:
                    filename = filename or "unknown"
                    line_number = line_number or 0
            
            # Get current datetime
            error_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert into database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO errors (error, filename, line_number, datetime)
                VALUES (?, ?, ?, ?)
            """, (error_message, filename, line_number, error_datetime))
            
            conn.commit()
            conn.close()
        except Exception as e:
            # Fallback to print if logging fails
            print(f"Warning: Failed to log error to database: {e}")
            print(f"Original error message: {error_message}")


# Global error logger instance
_error_logger_instance: Optional[ErrorLogger] = None


def get_error_logger() -> ErrorLogger:
    """Get or create the global error logger instance."""
    global _error_logger_instance
    if _error_logger_instance is None:
        _error_logger_instance = ErrorLogger()
    return _error_logger_instance


def log_error(error: Exception, filename: Optional[str] = None, line_number: Optional[int] = None) -> None:
    """Convenience function to log an error."""
    get_error_logger().log_error(error, filename, line_number)


def log_error_message(error_message: str, filename: Optional[str] = None, line_number: Optional[int] = None) -> None:
    """Convenience function to log an error message."""
    get_error_logger().log_error_message(error_message, filename, line_number)

