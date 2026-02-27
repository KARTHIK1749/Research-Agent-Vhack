"""
Performance monitoring and optimization service for MARIS.
"""
import time
import psutil
import threading
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PerformanceMetrics:
    """Performance metrics for a single operation."""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success: bool
    error_message: str = ""

class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.current_operations: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def start_operation(self, operation_name: str) -> str:
        """Start monitoring an operation."""
        with self.lock:
            operation_id = f"{operation_name}_{int(time.time() * 1000)}"
            self.current_operations[operation_id] = time.time()
            print(f"⏱️ Performance: Started {operation_name}")
            return operation_id
    
    def end_operation(self, operation_id: str, operation_name: str, success: bool = True, error_message: str = ""):
        """End monitoring an operation."""
        with self.lock:
            if operation_id in self.current_operations:
                start_time = self.current_operations.pop(operation_id)
                end_time = time.time()
                duration = end_time - start_time
                
                # Get system metrics
                memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
                cpu_usage = psutil.cpu_percent()
                
                metric = PerformanceMetrics(
                    operation_name=operation_name,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    memory_usage_mb=memory_usage,
                    cpu_usage_percent=cpu_usage,
                    success=success,
                    error_message=error_message
                )
                
                self.metrics.append(metric)
                
                status = "✅" if success else "❌"
                print(f"{status} Performance: {operation_name} completed in {duration:.2f}s")
                
                if not success:
                    print(f"❌ Performance: {operation_name} failed - {error_message}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics."""
        if not self.metrics:
            return {"message": "No metrics available"}
        
        # Group by operation name
        operation_stats = {}
        for metric in self.metrics:
            if metric.operation_name not in operation_stats:
                operation_stats[metric.operation_name] = {
                    "count": 0,
                    "total_duration": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_memory_mb": 0,
                    "avg_cpu_percent": 0,
                    "min_duration": float('inf'),
                    "max_duration": 0
                }
            
            stats = operation_stats[metric.operation_name]
            stats["count"] += 1
            stats["total_duration"] += metric.duration
            stats["avg_memory_mb"] += metric.memory_usage_mb
            stats["avg_cpu_percent"] += metric.cpu_usage_percent
            stats["min_duration"] = min(stats["min_duration"], metric.duration)
            stats["max_duration"] = max(stats["max_duration"], metric.duration)
            
            if metric.success:
                stats["successful"] += 1
            else:
                stats["failed"] += 1
        
        # Calculate averages
        for stats in operation_stats.values():
            if stats["count"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["count"]
                stats["avg_memory_mb"] /= stats["count"]
                stats["avg_cpu_percent"] /= stats["count"]
                stats["success_rate"] = (stats["successful"] / stats["count"]) * 100
            else:
                stats["avg_duration"] = 0
                stats["success_rate"] = 0
        
        return {
            "total_operations": len(self.metrics),
            "operation_stats": operation_stats,
            "system_info": {
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "memory_available_gb": psutil.virtual_memory().available / (1024**3),
                "cpu_count": psutil.cpu_count()
            }
        }
    
    def get_slow_operations(self, threshold_seconds: float = 5.0) -> List[Dict[str, Any]]:
        """Get operations that took longer than threshold."""
        slow_ops = []
        for metric in self.metrics:
            if metric.duration > threshold_seconds:
                slow_ops.append({
                    "operation_name": metric.operation_name,
                    "duration": metric.duration,
                    "timestamp": datetime.fromtimestamp(metric.start_time).isoformat(),
                    "success": metric.success,
                    "error_message": metric.error_message
                })
        
        return sorted(slow_ops, key=lambda x: x["duration"], reverse=True)
    
    def clear_metrics(self):
        """Clear all performance metrics."""
        with self.lock:
            self.metrics.clear()
            self.current_operations.clear()
            print("🧹 Performance: Metrics cleared")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(operation_name: str):
    """Decorator to monitor function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            operation_id = performance_monitor.start_operation(operation_name)
            try:
                result = func(*args, **kwargs)
                performance_monitor.end_operation(operation_id, operation_name, success=True)
                return result
            except Exception as e:
                performance_monitor.end_operation(operation_id, operation_name, success=False, error_message=str(e))
                raise
        return wrapper
    return decorator

def get_system_performance() -> Dict[str, Any]:
    """Get current system performance metrics."""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_gb": psutil.virtual_memory().used / (1024**3),
        "memory_available_gb": psutil.virtual_memory().available / (1024**3),
        "disk_usage_percent": psutil.disk_usage('/').percent if psutil.disk_usage('/') else 0
    }

def optimize_suggestions() -> List[str]:
    """Get performance optimization suggestions based on metrics."""
    suggestions = []
    summary = performance_monitor.get_metrics_summary()
    
    if "operation_stats" in summary:
        for op_name, stats in summary["operation_stats"].items():
            if stats["avg_duration"] > 10:
                suggestions.append(f"Consider caching results for {op_name} (avg: {stats['avg_duration']:.2f}s)")
            
            if stats["success_rate"] < 90:
                suggestions.append(f"Improve error handling for {op_name} (success rate: {stats['success_rate']:.1f}%)")
            
            if stats["avg_memory_mb"] > 1000:
                suggestions.append(f"Optimize memory usage for {op_name} (avg: {stats['avg_memory_mb']:.1f}MB)")
    
    system_perf = get_system_performance()
    if system_perf["memory_percent"] > 80:
        suggestions.append("High memory usage - consider clearing caches")
    
    if system_perf["cpu_percent"] > 80:
        suggestions.append("High CPU usage - consider reducing concurrent operations")
    
    return suggestions
