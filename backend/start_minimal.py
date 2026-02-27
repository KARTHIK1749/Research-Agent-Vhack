#!/usr/bin/env python3
"""
Minimal startup script that avoids all complex dependencies
"""
import os
import sys
import subprocess
from pathlib import Path

def check_env():
    """Check environment setup"""
    print("🔍 Checking environment...")
    
    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print("✅ .env file found")
        # Load and check for API key
        with open(env_file, 'r') as f:
            content = f.read()
            if "GOOGLE_API_KEY=" in content:
                print("✅ GOOGLE_API_KEY found in .env")
            else:
                print("❌ GOOGLE_API_KEY missing from .env")
                return False
    else:
        print("⚠️ .env file not found")
        # Check environment variable
        if os.getenv("GOOGLE_API_KEY"):
            print("✅ GOOGLE_API_KEY found in environment")
        else:
            print("❌ GOOGLE_API_KEY not found in environment")
            print("Please create .env file with: GOOGLE_API_KEY=your_key_here")
            return False
    
    return True

def start_with_direct_command():
    """Start server with direct command to avoid import issues"""
    try:
        print("🚀 Starting MARIS server with minimal imports...")
        
        # Use direct uvicorn command with app module
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ]
        
        print(f"🔧 Running: {' '.join(cmd)}")
        print("🌐 Server will be available at: http://localhost:8000")
        print("📖 API docs at: http://localhost:8000/docs")
        print("\n💡 If you see import errors, the server will still start")
        print("   and routes will load when first accessed\n")
        
        # Run the command
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        return False

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 MARIS (Multi-Agent Research Intelligence System)")
    print("=" * 60)
    
    # Check environment
    if not check_env():
        print("\n❌ Environment check failed")
        return False
    
    # Start server
    success = start_with_direct_command()
    
    if success:
        print("\n✅ Server completed successfully")
    else:
        print("\n❌ Server encountered issues")
        print("\n🔧 Troubleshooting steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set GOOGLE_API_KEY in .env file")
        print("3. Try: python start_simple.py")
        print("4. Try: python -m app.main")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
