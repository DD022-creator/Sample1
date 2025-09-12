# logs/log_manager.py
import logging
import json
from datetime import datetime, timedelta
import os
from .logging_config import get_logger

class LogManager:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.logger = get_logger("LogManager")
        self.processing_stats = {}
        self.current_stats_file = None
        
    def initialize_processing_session(self, audio_files):
        """Initialize a new processing session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_stats_file = os.path.join(self.log_dir, f"processing_stats_{timestamp}.json")
        
        self.processing_stats = {
            "session_id": timestamp,
            "start_time": datetime.now().isoformat(),
            "audio_files_to_process": len(audio_files),
            "audio_files_processed": 0,
            "audio_files_failed": 0,
            "total_detections": 0,
            "detections_by_class": {
                "1": {"name": "vessel", "count": 0},
                "2": {"name": "marine_animal", "count": 0},
                "3": {"name": "natural_sound", "count": 0},
                "4": {"name": "other_anthropogenic", "count": 0}
            },
            "processing_times": {
                "total_processing_time": 0,
                "average_time_per_file": 0,
                "file_processing_times": {}
            },
            "confidence_statistics": {
                "average_confidence": 0,
                "min_confidence": 1.0,
                "max_confidence": 0.0,
                "confidence_distribution": []
            },
            "errors": [],
            "warnings": []
        }
        
        self._save_stats()
        self.logger.info(f"Processing session initialized: {timestamp}")
        
    def log_file_processing_start(self, audio_file, file_size, duration):
        """Log the start of file processing"""
        self.processing_stats["processing_times"]["file_processing_times"][audio_file] = {
            "start_time": datetime.now().isoformat(),
            "file_size": file_size,
            "duration": duration,
            "status": "processing"
        }
        self._save_stats()
        
    def log_file_processing_end(self, audio_file, detections, processing_time):
        """Log the end of file processing"""
        if audio_file in self.processing_stats["processing_times"]["file_processing_times"]:
            file_stats = self.processing_stats["processing_times"]["file_processing_times"][audio_file]
            file_stats["end_time"] = datetime.now().isoformat()
            file_stats["processing_time_seconds"] = processing_time
            file_stats["detections_count"]: len(detections)
            file_stats["status"] = "completed"
            file_stats["detections"] = detections
            
            # Update overall statistics
            self.processing_stats["audio_files_processed"] += 1
            self.processing_stats["total_detections"] += len(detections)
            self.processing_stats["processing_times"]["total_processing_time"] += processing_time
            
            # Update class-specific counts
            for detection in detections:
                class_id = str(detection.get('category_id', 'unknown'))
                confidence = detection.get('score', 0)
                
                if class_id in self.processing_stats["detections_by_class"]:
                    self.processing_stats["detections_by_class"][class_id]["count"] += 1
                
                # Update confidence statistics
                self.processing_stats["confidence_statistics"]["min_confidence"] = min(
                    self.processing_stats["confidence_statistics"]["min_confidence"], 
                    confidence
                )
                self.processing_stats["confidence_statistics"]["max_confidence"] = max(
                    self.processing_stats["confidence_statistics"]["max_confidence"], 
                    confidence
                )
                self.processing_stats["confidence_statistics"]["confidence_distribution"].append(confidence)
            
            # Calculate averages
            if self.processing_stats["audio_files_processed"] > 0:
                self.processing_stats["processing_times"]["average_time_per_file"] = (
                    self.processing_stats["processing_times"]["total_processing_time"] / 
                    self.processing_stats["audio_files_processed"]
                )
                
            if self.processing_stats["total_detections"] > 0:
                total_confidence = sum(self.processing_stats["confidence_statistics"]["confidence_distribution"])
                self.processing_stats["confidence_statistics"]["average_confidence"] = (
                    total_confidence / self.processing_stats["total_detections"]
                )
            
            self._save_stats()
            self.logger.info(f"Processed {audio_file}: {len(detections)} detections in {processing_time:.2f}s")
    
    def log_error(self, audio_file, error_message, error_type="processing"):
        """Log an error"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "audio_file": audio_file,
            "error_type": error_type,
            "message": error_message
        }
        
        self.processing_stats["errors"].append(error_entry)
        self.processing_stats["audio_files_failed"] += 1
        
        if audio_file in self.processing_stats["processing_times"]["file_processing_times"]:
            self.processing_stats["processing_times"]["file_processing_times"][audio_file]["status"] = "failed"
        
        self._save_stats()
        self.logger.error(f"Error processing {audio_file}: {error_message}")
    
    def log_warning(self, audio_file, warning_message):
        """Log a warning"""
        warning_entry = {
            "timestamp": datetime.now().isoformat(),
            "audio_file": audio_file,
            "message": warning_message
        }
        
        self.processing_stats["warnings"].append(warning_entry)
        self._save_stats()
        self.logger.warning(f"Warning for {audio_file}: {warning_message}")
    
    def finalize_session(self):
        """Finalize the processing session"""
        self.processing_stats["end_time"] = datetime.now().isoformat()
        self.processing_stats["total_processing_time"] = (
            datetime.fromisoformat(self.processing_stats["end_time"]) - 
            datetime.fromisoformat(self.processing_stats["start_time"])
        ).total_seconds()
        
        self.processing_stats["success_rate"] = (
            self.processing_stats["audio_files_processed"] / 
            self.processing_stats["audio_files_to_process"] * 100
            if self.processing_stats["audio_files_to_process"] > 0 else 0
        )
        
        self._save_stats()
        
        # Generate summary log
        summary = self._generate_summary()
        self.logger.info(f"Processing session completed: {summary}")
        
        return summary
    
    def _generate_summary(self):
        """Generate a summary of the processing session"""
        return (
            f"Files processed: {self.processing_stats['audio_files_processed']}/"
            f"{self.processing_stats['audio_files_to_process']} "
            f"({self.processing_stats.get('success_rate', 0):.1f}%), "
            f"Detections: {self.processing_stats['total_detections']}, "
            f"Time: {self.processing_stats.get('total_processing_time', 0):.2f}s"
        )
    
    def _save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.current_stats_file, 'w') as f:
                json.dump(self.processing_stats, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save statistics: {e}")