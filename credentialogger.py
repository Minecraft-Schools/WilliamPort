import json
import datetime
import os
from typing import Optional, Dict, Any

class CredentialLogger:
    def __init__(self, log_file_path: str = None):
        """
        Initialize the credential logger.
        
        Args:
            log_file_path: Path to the log file. If None, uses default path.
        """
        if log_file_path is None:
            # Use the same directory structure as main.py
            main_dir = '/Users/williamgroh/Desktop/http-server/dict/main/'
            self.log_file_path = main_dir + 'signin/credential_logs.json'
        else:
            self.log_file_path = log_file_path
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        
        # Initialize log file if it doesn't exist
        if not os.path.exists(self.log_file_path):
            self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Initialize an empty log file with proper structure."""
        initial_data = {
            "logs": [],
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_entries": 0
        }
        
        with open(self.log_file_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    def _load_logs(self) -> Dict[str, Any]:
        """Load existing logs from file."""
        try:
            with open(self.log_file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._initialize_log_file()
            return self._load_logs()
    
    def _save_logs(self, data: Dict[str, Any]):
        """Save logs to file."""
        with open(self.log_file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def log_credentials(self, userid: int, password: str, additional_info: Optional[Dict] = None) -> bool:
        """
        Log user credentials to the file.
        
        Args:
            userid: The user ID
            password: The user's password (will be stored as-is - consider security implications)
            additional_info: Optional dictionary with additional information to log
            
        Returns:
            bool: True if logging was successful, False otherwise
        """
        try:
            # Load existing logs
            log_data = self._load_logs()
            
            # Create new log entry
            log_entry = {
                "userid": userid,
                "password": password,  # WARNING: Storing passwords in plaintext
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "ip_address": None,  # Could be populated if available
                "user_agent": None,  # Could be populated if available
            }
            
            # Add additional info if provided
            if additional_info:
                log_entry.update(additional_info)
            
            # Add to logs
            log_data["logs"].append(log_entry)
            log_data["total_entries"] = len(log_data["logs"])
            log_data["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            # Save to file
            self._save_logs(log_data)
            
            return True
            
        except Exception as e:
            print(f"Error logging credentials: {e}")
            return False
    
    def get_logs_by_userid(self, userid: int) -> list:
        """
        Retrieve all log entries for a specific user ID.
        
        Args:
            userid: The user ID to search for
            
        Returns:
            list: List of log entries for the specified user
        """
        try:
            log_data = self._load_logs()
            return [log for log in log_data["logs"] if log["userid"] == userid]
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return []
    
    def get_recent_logs(self, limit: int = 10) -> list:
        """
        Get the most recent log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            list: List of recent log entries
        """
        try:
            log_data = self._load_logs()
            return log_data["logs"][-limit:]
        except Exception as e:
            print(f"Error retrieving recent logs: {e}")
            return []
    
    def clear_logs(self) -> bool:
        """
        Clear all log entries.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._initialize_log_file()
            return True
        except Exception as e:
            print(f"Error clearing logs: {e}")
            return False

# Convenience functions for backward compatibility and ease of use
_default_logger = None

def get_default_logger() -> CredentialLogger:
    """Get the default credential logger instance."""
    global _default_logger
    if _default_logger is None:
        _default_logger = CredentialLogger()
    return _default_logger

def log_user_credentials(userid: int, password: str, additional_info: Optional[Dict] = None) -> bool:
    """
    Convenience function to log user credentials using the default logger.
    
    Args:
        userid: The user ID
        password: The user's password
        additional_info: Optional additional information to log
        
    Returns:
        bool: True if logging was successful, False otherwise
    """
    logger = get_default_logger()
    return logger.log_credentials(userid, password, additional_info)

def get_user_login_history(userid: int) -> list:
    """
    Convenience function to get login history for a user.
    
    Args:
        userid: The user ID
        
    Returns:
        list: List of log entries for the user
    """
    logger = get_default_logger()
    return logger.get_logs_by_userid(userid)

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    logger = CredentialLogger()
    
    # Log some credentials
    success = logger.log_credentials(
        userid=12345, 
        password="user_password_123",
        additional_info={
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "login_method": "web_form"
        }
    )
    
    if success:
        print("Credentials logged successfully")
    else:
        print("Failed to log credentials")
    
    # Retrieve logs for a user
    user_logs = logger.get_logs_by_userid(12345)
    print(f"Found {len(user_logs)} log entries for user 12345")
    
    # Get recent logs
    recent = logger.get_recent_logs(5)
    print(f"Recent logs: {len(recent)} entries")