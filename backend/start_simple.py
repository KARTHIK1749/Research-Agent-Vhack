#!/usr/bin/env python3
"""
Simple startup script that avoids complex import chains
"""
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

def check_environment():
    """Check if environment variables are set"""
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found!")
        print("Please set: export GOOGLE_API_KEY=your_key_here")
        print("Or create a .env file with: GOOGLE_API_KEY=your_key_here")
        return False
    print("✅ Environment variables found")
    return True

def start_server():
    """Start the server with minimal imports"""
    try:
        print("🚀 Starting MARIS server...")
        
        # Check environment first
        if not check_environment():
            return False
            
        # Import and start server
        print("📦 Loading modules...")
        import uvicorn
        from app.main import app
        
        print("🌐 Starting FastAPI server...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Server failed to start: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check if GOOGLE_API_KEY is set correctly")
        print("3. Try running: python -m app.main")
        return False

if __name__ == "__main__":
    success = start_server()
    if not success:
        sys.exit(1)
