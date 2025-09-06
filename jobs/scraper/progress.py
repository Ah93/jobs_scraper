import json
import os
import time
from typing import Dict, Any

class ProgressTracker:
    """Simple progress tracker for scraping operations"""
    
    def __init__(self, operation_id: str):
        self.operation_id = operation_id
        self.progress_file = f"progress_{operation_id}.json"
        self.start_time = time.time()
        
    def update(self, stage: str, current: int, total: int, message: str = ""):
        """Update progress"""
        progress_data = {
            "operation_id": self.operation_id,
            "stage": stage,
            "current": current,
            "total": total,
            "percentage": int((current / total) * 100) if total > 0 else 0,
            "message": message,
            "elapsed_time": time.time() - self.start_time,
            "timestamp": time.time()
        }
        
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f)
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    def complete(self, message: str = "Operation completed"):
        """Mark operation as complete"""
        self.update("completed", 100, 100, message)
        
    def error(self, message: str = "Operation failed"):
        """Mark operation as failed"""
        self.update("error", 0, 100, message)
    
    def cleanup(self):
        """Clean up progress file"""
        try:
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
        except Exception as e:
            print(f"Error cleaning up progress file: {e}")

def get_progress(operation_id: str) -> Dict[str, Any]:
    """Get current progress for an operation"""
    progress_file = f"progress_{operation_id}.json"
    try:
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error reading progress: {e}")
    
    return {
        "operation_id": operation_id,
        "stage": "unknown",
        "current": 0,
        "total": 100,
        "percentage": 0,
        "message": "Progress not available",
        "elapsed_time": 0,
        "timestamp": time.time()
    }
