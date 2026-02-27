#!/usr/bin/env python3
"""
Start backend with debug information and error handling.
"""
import os
import sys
import traceback

# Set environment variables for performance
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTHONOPTIMIZE"] = "1"

def main():
    print("🚀 Starting MARIS Backend with Debug...")
    
    try:
        # Check if we're in the right directory
        if not os.path.exists("app/main.py"):
            print("❌ Error: app/main.py not found!")
            print("💡 Make sure you're running this from the backend directory")
            return False
        
        # Try to import the app
        print("📦 Importing FastAPI app...")
        from app.main import app
        print("✅ FastAPI app imported successfully")
        
        # Start the server
        print("🌐 Starting server on http://localhost:8000")
        print("📊 API docs will be available at http://localhost:8000/docs")
        print("🔍 Health check at http://localhost:8000/health")
        print("⚡ Press Ctrl+C to stop the server")
        print("-" * 50)
        
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n🔧 Possible fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Check if you're in the backend directory")
        print("3. Check your PYTHONPATH")
        return False
        
    except OSError as e:
        if "10048" in str(e) or "already in use" in str(e):
            print(f"❌ Port 8000 is already in use!")
            print("\n🔧 Fix:")
            print("1. Find the process: netstat -ano | findstr :8000")
            print("2. Kill it: taskkill /F /PID <PID>")
            print("3. Try again")
        else:
            print(f"❌ System Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 For more help, run: python diagnose_backend.py")
        sys.exit(1)
