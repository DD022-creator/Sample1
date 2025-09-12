# logs/log_rotation.py
import os
import glob
import json
from datetime import datetime, timedelta

def rotate_logs(log_dir="logs", max_age_days=30, max_files=100):
    """
    Rotate and clean up old log files
    """
    # Get all log files
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    json_files = glob.glob(os.path.join(log_dir, "*.json"))
    
    all_files = log_files + json_files
    
    # Sort files by modification time (oldest first)
    all_files.sort(key=os.path.getmtime)
    
    current_time = datetime.now()
    files_deleted = 0
    
    for file_path in all_files:
        # Check file age
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        file_age = (current_time - file_mtime).days
        
        # Delete files older than max_age_days
        if file_age > max_age_days:
            try:
                os.remove(file_path)
                files_deleted += 1
                print(f"Deleted old log file: {os.path.basename(file_path)} ({file_age} days old)")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        
        # Also enforce maximum number of files
        if len(all_files) - files_deleted > max_files:
            try:
                os.remove(file_path)
                files_deleted += 1
                print(f"Deleted log file to enforce limit: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    
    # Create a summary of the rotation
    rotation_summary = {
        "rotation_time": current_time.isoformat(),
        "files_deleted": files_deleted,
        "remaining_files": len(all_files) - files_deleted,
        "max_age_days": max_age_days,
        "max_files": max_files
    }
    
    # Save rotation summary
    summary_file = os.path.join(log_dir, "log_rotation_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(rotation_summary, f, indent=2)
    
    return rotation_summary

if __name__ == "__main__":
    summary = rotate_logs()
    print(f"Log rotation completed: {summary['files_deleted']} files deleted")