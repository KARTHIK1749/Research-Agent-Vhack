#!/usr/bin/env python3
"""
Start backend on port 8001 to avoid conflicts.
"""
import os
import sys

# Set environment variables for performance
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTHONOPTIMIZE"] = "1"

def main():
    print("🚀 Starting MARIS Backend on Port 8001...")
    
    try:
        # Import the app
        from app.main import app
        print("✅ FastAPI app imported successfully")
        
        # Start the server on port 8001
        print("🌐 Starting server on http://localhost:8001")
        print("📊 API docs will be available at http://localhost:8001/docs")
        print("🔍 Health check at http://localhost:8001/health")
        print("⚡ Press Ctrl+C to stop the server")
        print("-" * 50)
        
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,  # Use port 8001
            reload=False,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
