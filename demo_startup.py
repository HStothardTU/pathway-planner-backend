#!/usr/bin/env python3
"""
Demo Startup Script for Pathway Planner
This script helps you start both backend and frontend for the demo.
"""

import subprocess
import time
import sys
import os

def print_banner():
    print("=" * 60)
    print("🚀 PATHWAY PLANNER DEMO STARTUP")
    print("=" * 60)
    print("Teesside Transport Decarbonization Tool")
    print("=" * 60)

def check_dependencies():
    print("🔍 Checking dependencies...")
    
    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Error: Please run this script from the project root directory")
        print("   (where app/main.py exists)")
        sys.exit(1)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
        print("   Consider activating your virtual environment first")
    
    print("✅ Dependencies check complete")

def start_backend():
    print("\n🔧 Starting Backend (FastAPI)...")
    print("   Backend will be available at: http://localhost:8000")
    print("   API docs at: http://localhost:8000/docs")
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Backend started successfully")
        return backend_process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    print("\n🎨 Starting Frontend (Streamlit)...")
    print("   Frontend will be available at: http://localhost:8501")
    
    try:
        # Change to frontend directory
        os.chdir("pathway-planner-frontend")
        
        # Start frontend in background
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501", "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Change back to root directory
        os.chdir("..")
        
        print("✅ Frontend started successfully")
        return frontend_process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    print_banner()
    check_dependencies()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Wait a moment for backend to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(3)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 DEMO IS READY!")
    print("=" * 60)
    print("📊 Dashboard: http://localhost:8501")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    print("\n💡 Demo Instructions:")
    print("1. Open http://localhost:8501 in your browser")
    print("2. Click '🚀 Load Demo Scenarios' in Scenario Builder")
    print("3. Go to Visualize Pathways and click '🚀 Load Demo Data'")
    print("4. Click '⚡ Run Optimization' to see the magic!")
    print("\n🛑 Press Ctrl+C to stop both services")
    print("=" * 60)
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ Services stopped")

if __name__ == "__main__":
    main() 