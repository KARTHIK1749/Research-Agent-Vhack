"""
Progress tracking service for real-time UI updates.
Tracks the status of each processing step and provides detailed progress information.
"""
import time
import threading
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class ProcessingStatus(Enum):
    """Processing status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class StepProgress:
    """Progress information for a single step."""
    step_name: str
    status: ProcessingStatus
    start_time: float = None
    end_time: float = None
    duration: float = None
    progress_percentage: float = 0.0
    current_operation: str = ""
    details: Dict[str, Any] = None
    error_message: str = ""
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

class ProgressTracker:
    """Tracks progress across all processing steps."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.steps: Dict[str, StepProgress] = {}
        self.current_step: str = None
        self.lock = threading.Lock()
        self.listeners: List[callable] = []
        
        # Initialize all steps
        self._initialize_steps()
    
    def _initialize_steps(self):
        """Initialize all processing steps with their display names."""
        step_info = {
            "meta": {
                "display_name": "Query Optimization",
                "description": "Optimizing search query for better results",
                "icon": "🧠"
            },
            "literature": {
                "display_name": "Literature Review", 
                "description": "Fetching and analyzing research papers",
                "icon": "📚"
            },
            "related_work": {
                "display_name": "Related Work Analysis",
                "description": "Analyzing related research and identifying connections",
                "icon": "🔗"
            },
            "gap": {
                "display_name": "Gap Detection",
                "description": "Identifying research gaps using cluster analysis",
                "icon": "🎯"
            },
            "experiment": {
                "display_name": "Experiment Design",
                "description": "Designing experiments and calculating research scores",
                "icon": "🧪"
            },
            "reflection": {
                "display_name": "Self-Reflection",
                "description": "Refining hypotheses and improving research design",
                "icon": "🔄"
            },
            "dataset": {
                "display_name": "Dataset Recommendation",
                "description": "Finding suitable datasets for experiments",
                "icon": "📊"
            },
            "draft": {
                "display_name": "Paper Drafting",
                "description": "Generating research paper draft",
                "icon": "📝"
            }
        }
        
        for step_key, info in step_info.items():
            self.steps[step_key] = StepProgress(
                step_name=step_key,
                status=ProcessingStatus.PENDING,
                details=info
            )
    
    def start_step(self, step_name: str, operation: str = ""):
        """Start processing a step."""
        with self.lock:
            if step_name in self.steps:
                step = self.steps[step_name]
                step.status = ProcessingStatus.RUNNING
                step.start_time = time.time()
                step.current_operation = operation
                step.progress_percentage = 0.0
                step.error_message = ""
                self.current_step = step_name
                self._notify_listeners()
    
    def update_progress(self, step_name: str, percentage: float, operation: str = "", details: Dict[str, Any] = None):
        """Update progress for a step."""
        with self.lock:
            if step_name in self.steps:
                step = self.steps[step_name]
                step.progress_percentage = min(100.0, max(0.0, percentage))
                if operation:
                    step.current_operation = operation
                if details:
                    step.details.update(details)
                self._notify_listeners()
    
    def complete_step(self, step_name: str, details: Dict[str, Any] = None):
        """Mark a step as completed."""
        with self.lock:
            if step_name in self.steps:
                step = self.steps[step_name]
                step.status = ProcessingStatus.COMPLETED
                step.end_time = time.time()
                step.progress_percentage = 100.0
                step.current_operation = "Completed"
                if details:
                    step.details.update(details)
                if step.start_time:
                    step.duration = step.end_time - step.start_time
                self._notify_listeners()
    
    def fail_step(self, step_name: str, error_message: str, details: Dict[str, Any] = None):
        """Mark a step as failed."""
        with self.lock:
            if step_name in self.steps:
                step = self.steps[step_name]
                step.status = ProcessingStatus.FAILED
                step.end_time = time.time()
                step.error_message = error_message
                step.current_operation = "Failed"
                if details:
                    step.details.update(details)
                if step.start_time:
                    step.duration = step.end_time - step.start_time
                self._notify_listeners()
    
    def skip_step(self, step_name: str, reason: str = ""):
        """Skip a step."""
        with self.lock:
            if step_name in self.steps:
                step = self.steps[step_name]
                step.status = ProcessingStatus.SKIPPED
                step.end_time = time.time()
                step.progress_percentage = 100.0
                step.current_operation = f"Skipped: {reason}" if reason else "Skipped"
                if step.start_time:
                    step.duration = step.end_time - step.start_time
                self._notify_listeners()
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of all progress."""
        with self.lock:
            total_steps = len(self.steps)
            completed_steps = sum(1 for step in self.steps.values() if step.status == ProcessingStatus.COMPLETED)
            failed_steps = sum(1 for step in self.steps.values() if step.status == ProcessingStatus.FAILED)
            running_steps = sum(1 for step in self.steps.values() if step.status == ProcessingStatus.RUNNING)
            
            overall_progress = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
            
            return {
                "session_id": self.session_id,
                "overall_progress": overall_progress,
                "total_steps": total_steps,
                "completed_steps": completed_steps,
                "failed_steps": failed_steps,
                "running_steps": running_steps,
                "current_step": self.current_step,
                "steps": {name: self._step_to_dict(step) for name, step in self.steps.items()},
                "timestamp": datetime.now().isoformat()
            }
    
    def _step_to_dict(self, step: StepProgress) -> Dict[str, Any]:
        """Convert StepProgress to dictionary."""
        return {
            "step_name": step.step_name,
            "status": step.status.value,
            "display_name": step.details.get("display_name", step.step_name),
            "description": step.details.get("description", ""),
            "icon": step.details.get("icon", "⚙️"),
            "progress_percentage": step.progress_percentage,
            "current_operation": step.current_operation,
            "duration": step.duration,
            "error_message": step.error_message,
            "details": {k: v for k, v in step.details.items() if k not in ["display_name", "description", "icon"]}
        }
    
    def add_listener(self, callback: callable):
        """Add a progress listener."""
        self.listeners.append(callback)
    
    def remove_listener(self, callback: callable):
        """Remove a progress listener."""
        if callback in self.listeners:
            self.listeners.remove(callback)
    
    def _notify_listeners(self):
        """Notify all listeners of progress changes."""
        summary = self.get_progress_summary()
        for listener in self.listeners:
            try:
                listener(summary)
            except Exception as e:
                print(f"Error notifying progress listener: {str(e)}")

# Global progress trackers
_progress_trackers: Dict[str, ProgressTracker] = {}
_tracker_lock = threading.Lock()

def get_progress_tracker(session_id: str) -> ProgressTracker:
    """Get or create a progress tracker for a session."""
    with _tracker_lock:
        if session_id not in _progress_trackers:
            _progress_trackers[session_id] = ProgressTracker(session_id)
        return _progress_trackers[session_id]

def remove_progress_tracker(session_id: str):
    """Remove a progress tracker."""
    with _tracker_lock:
        if session_id in _progress_trackers:
            del _progress_trackers[session_id]

# Decorator for automatic progress tracking
def track_step_progress(step_name: str, operations: List[str] = None):
    """Decorator to automatically track step progress."""
    def decorator(func):
        def wrapper(state: Dict[str, Any], *args, **kwargs):
            session_id = state.get("session_id", "default")
            tracker = get_progress_tracker(session_id)
            
            try:
                # Start step
                tracker.start_step(step_name, operations[0] if operations else f"Running {step_name}")
                
                # Update progress through operations
                if operations:
                    for i, operation in enumerate(operations[1:], 1):
                        progress = (i / len(operations)) * 100
                        tracker.update_progress(step_name, progress, operation)
                
                # Execute the function
                result = func(state, *args, **kwargs)
                
                # Complete step
                tracker.complete_step(step_name, {"result": "success"})
                return result
                
            except Exception as e:
                # Fail step
                tracker.fail_step(step_name, str(e))
                raise
        
        return wrapper
    return decorator
