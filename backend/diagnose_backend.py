#!/usr/bin/env python3
"""
Backend diagnostic script to identify and fix issues.
"""
import os
import sys
import requests
from pathlib import Path

def check_environment():
    """Check environment setup."""
    print("🔍 Checking Environment Setup...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("💡 Create .env file from env.example.txt")
        return False
    
    print("✅ .env file exists")
    
    # Check API key
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            if "GOOGLE_API_KEY=" in content and "your api key here" not in content:
                print("✅ GOOGLE_API_KEY appears to be set")
            else:
                print("❌ GOOGLE_API_KEY not properly set!")
                print("💡 Edit .env file and add your Google API key")
                return False
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False
    
    return True

def check_dependencies():
    """Check Python dependencies."""
    print("\n🔍 Checking Dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'langgraph', 
        'langchain', 'sentence-transformers', 'google-generativeai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_imports():
    """Check critical imports."""
    print("\n🔍 Checking Critical Imports...")
    
    try:
        # Test core imports
        from app.main import app
        print("✅ FastAPI app import")
        
        from app.services.gemini_service import test_gemini_connection
        print("✅ Gemini service import")
        
        from app.agents.literature_agent import run as literature_run
        print("✅ Literature agent import")
        
        from app.api.routes import router
        print("✅ API routes import")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_gemini_api():
    """Test Gemini API connection."""
    print("\n🔍 Testing Gemini API...")
    
    try:
        from app.services.gemini_service import test_gemini_connection
        result = test_gemini_connection()
        
        if result:
            print("✅ Gemini API connection successful")
            return True
        else:
            print("❌ Gemini API connection failed")
            print("💡 Check your GOOGLE_API_KEY in .env file")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test error: {e}")
        return False

def check_port_availability():
    """Check if port 8000 is available."""
    print("\n🔍 Checking Port Availability...")
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result == 0:
        print("❌ Port 8000 is already in use!")
        print("💡 Kill the process or use a different port")
        
        # Try to find what's using the port
        try:
            import subprocess
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if ':8000' in line and 'LISTENING' in line:
                    print(f"🔍 Found process: {line.strip()}")
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        print(f"💡 Kill with: taskkill /F /PID {pid}")
        except:
            pass
        
        return False
    else:
        print("✅ Port 8000 is available")
        return True

def create_cache_directories():
    """Create necessary cache directories."""
    print("\n🔍 Creating Cache Directories...")
    
    directories = ['./cache', './data/vector_db']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}")

def fix_common_issues():
    """Fix common backend issues."""
    print("\n🔧 Fixing Common Issues...")
    
    # Fix 1: Ensure proper Python path
    current_dir = Path.cwd()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
        print("✅ Added current directory to Python path")
    
    # Fix 2: Set environment variables
    os.environ.setdefault('PYTHONPATH', str(current_dir))
    print("✅ Set PYTHONPATH environment variable")

def run_health_check():
    """Run backend health check if server is running."""
    print("\n🔍 Running Health Check...")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            print(f"📊 Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Run complete diagnostic."""
    print("🚀 MARIS Backend Diagnostic Tool")
    print("=" * 50)
    
    # Change to backend directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run all checks
    checks = [
        ("Environment", check_environment),
        ("Dependencies", check_dependencies),
        ("Imports", check_imports),
        ("Gemini API", test_gemini_api),
        ("Port Availability", check_port_availability),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check crashed: {e}")
            all_passed = False
    
    # Fix common issues
    fix_common_issues()
    create_cache_directories()
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Backend should work properly.")
        print("\n🚀 To start the backend:")
        print("   python start_fast.py")
        print("   # OR")
        print("   python start_minimal.py")
    else:
        print("⚠️ Some checks failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("   1. Set GOOGLE_API_KEY in .env file")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Kill process using port 8000")
    
    # Try health check if backend might be running
    try:
        run_health_check()
    except:
        pass
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
