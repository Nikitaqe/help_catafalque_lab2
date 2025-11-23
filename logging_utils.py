import os
import datetime

LOG_FILE = "shell.log"

def setup_logging():
    """Инициализация файла лога"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n=== Shell started at {datetime.datetime.now()} ===\n")

def log_command(command, success=True, error_msg=""):
    """Логирование команды"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {command}\n")
        if not success:
            f.write(f"[{timestamp}] ERROR: {error_msg}\n")