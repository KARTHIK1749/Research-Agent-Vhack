#!/usr/bin/env python3
"""
Performance monitoring script.
"""
import requests
import time
import json

def monitor_performance():
    """Monitor backend performance."""
    try:
        # Check system performance
        response = requests.get("http://localhost:8000/api/performance/system", timeout=5)
        if response.ok:
            print("📊 System Performance:")
            print(json.dumps(response.json(), indent=2))
        
        # Check performance stats
        response = requests.get("http://localhost:8000/api/performance/stats", timeout=5)
        if response.ok:
            print("\n📈 Performance Stats:")
            stats = response.json()
            print(f"Total operations: {stats.get('total_operations', 0)}")
            
            if 'operation_stats' in stats:
                for op, data in stats['operation_stats'].items():
                    if data.get('avg_duration', 0) > 0:
                        print(f"  {op}: {data['avg_duration']:.2f}s avg")
        
    except Exception as e:
        print(f"❌ Monitoring failed: {str(e)}")
        print("💡 Make sure backend is running on http://localhost:8000")

if __name__ == "__main__":
    monitor_performance()
