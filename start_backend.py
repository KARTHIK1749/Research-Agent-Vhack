#!/usr/bin/env python3
"""
Start MARIS Backend on Port 8000
"""
import os
import sys

# Change to backend directory
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)

# Add backend directory to Python path
sys.path.insert(0, backend_dir)

# Set environment variables for performance
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTHONOPTIMIZE"] = "1"

print("🚀 Starting MARIS Backend on Port 8000...")
print("📍 Backend will be available at: http://localhost:8000")
print("📊 API docs at: http://localhost:8000/docs")
print("🔍 Health check at: http://localhost:8000/health")
print("-" * 50)

try:
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
except Exception as e:
    print(f"❌ Error starting backend: {e}")
    sys.exit(1)
