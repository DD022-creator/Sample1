# logs/logging_config.py
import logging
import os
from datetime import datetime
import json

def setup_logging(log_dir="logs", log_level=logging.INFO):
    """
    Set up logging configuration for the underwater sound analyzer
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a timestamp for log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Log file paths
    log_file = os.path.join(log_dir, f"audio_analysis_{timestamp}.log")
    error_file = os.path.join(log_dir, f"errors_{timestamp}.log")
    processing_file = os.path.join(log_dir, f"processing_stats_{timestamp}.json")
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # File handler for errors only
    error_handler = logging.FileHandler(error_file)
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    # Create a dictionary to track processing statistics
    processing_stats = {
        "start_time": datetime.now().isoformat(),
        "audio_files_processed": 0,
        "total_detections": 0,
        "detections_by_class": {
            "vessel": 0,
            "marine_animal": 0,
            "natural_sound": 0,
            "other_anthropogenic": 0
        },
        "processing_times": {},
        "errors": []
    }
    
    # Save initial processing stats
    with open(processing_file, 'w') as f:
        json.dump(processing_stats, f, indent=2)
    
    return processing_file

def get_logger(name):
    """Get a logger with the given name"""
    return logging.getLogger(name)

def log_processing_stats(stats_file, stats_data):
    """Update processing statistics"""
    try:
        with open(stats_file, 'r') as f:
            current_stats = json.load(f)
        
        # Update statistics
        current_stats.update(stats_data)
        
        with open(stats_file, 'w') as f:
            json.dump(current_stats, f, indent=2)
            
    except Exception as e:
        logging.error(f"Failed to update processing stats: {e}")

def log_error(stats_file, error_message, audio_file=None):
    """Log an error to the statistics file"""
    try:
        with open(stats_file, 'r') as f:
            current_stats = json.load(f)
        
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": error_message,
            "audio_file": audio_file
        }
        
        current_stats["errors"].append(error_entry)
        
        with open(stats_file, 'w') as f:
            json.dump(current_stats, f, indent=2)
            
    except Exception as e:
        print(f"Failed to log error: {e}")