#!/usr/bin/env python3
"""
Start MARIS Frontend on Port 8173
"""
import os
import sys
import subprocess

# Change to frontend directory
frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
os.chdir(frontend_dir)

print("🎨 Starting MARIS Frontend on Port 8173...")
print("📍 Frontend will be available at: http://localhost:8173")
print("🔗 Backend should be running at: http://localhost:8000")
print("-" * 50)

try:
    # Start npm dev server
    subprocess.run(["npm", "run", "dev"], check=True)
except subprocess.CalledProcessError as e:
    print(f"❌ Error starting frontend: {e}")
    print("💡 Make sure you have run 'npm install' in the frontend directory")
    sys.exit(1)
except FileNotFoundError:
    print("❌ npm not found. Please install Node.js and npm")
    sys.exit(1)
