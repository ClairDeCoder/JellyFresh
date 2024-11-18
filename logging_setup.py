import logging
import os
from datetime import datetime, timedelta
import glob

def setup_logging(LOG_DIR):
    """Setup logging for each scan with a timestamped log file and limit to the most recent 6 logs."""
    
    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)
    os.chmod(LOG_DIR, 0o755)

    # Create a timestamped log file for this scan
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f'jellyfin_new_releases_{timestamp}.log')

    # Configure the logger to write to the new log file
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Initialize the root logger with the new handler
    root_logger = logging.getLogger()
    root_logger.handlers = []  # Clear any existing handlers
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    # Console output for real-time viewing
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.info("Logging setup complete.")

    # Limit to 6 most recent log files
    cleanup_old_logs(LOG_DIR)

def cleanup_old_logs(LOG_DIR):
    """Delete older logs, keeping only the most recent 6."""
    log_files = sorted(glob.glob(os.path.join(LOG_DIR, "jellyfin_new_releases_*.log")), reverse=True)
    for old_log in log_files[6:]:
        os.remove(old_log)