#!/usr/bin/env python3
"""
Enhanced startup script for tubeMate that automatically handles port conflicts.
This script will find available ports and start the service gracefully.
"""

import os
import sys
import socket
import subprocess
import time
from logging_config import setup_logging, log_step, log_success, log_error, log_warning

def find_available_port(start_port=7860, max_attempts=100):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    
    # If no port found in range, try system-assigned port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 0))
        port = s.getsockname()[1]
        return port

def check_port_in_use(port):
    """Check if a port is currently in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return False
    except OSError:
        return True

def kill_process_on_port(port):
    """Try to kill process using the specified port (Windows/Unix compatible)"""
    try:
        if os.name == 'nt':  # Windows
            # Use netstat to find PID
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        log_warning(f"Found process {pid} using port {port}, attempting to terminate...")
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        time.sleep(2)
                        return True
        else:  # Unix/Linux/macOS
            # Use lsof to find and kill process
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pid = result.stdout.strip()
                log_warning(f"Found process {pid} using port {port}, attempting to terminate...")
                subprocess.run(['kill', '-9', pid], capture_output=True)
                time.sleep(2)
                return True
    except Exception as e:
        log_error(f"Could not kill process on port {port}: {e}")
    
    return False

def start_tubeMate():
    """Start tubeMate with intelligent port handling"""
    setup_logging()
    
    print("🎬 tubeMate - Smart Startup with Port Detection")
    print("=" * 60)
    
    # Check if port 7860 is available
    if check_port_in_use(7860):
        log_warning("Port 7860 is already in use!")
        
        # Ask user what to do
        print("\nOptions:")
        print("1. Find and use an alternative port")
        print("2. Try to terminate the process using port 7860")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "2":
            log_step("Attempting to free port 7860...")
            if kill_process_on_port(7860):
                log_success("Successfully freed port 7860!")
                time.sleep(1)
                if not check_port_in_use(7860):
                    log_success("Port 7860 is now available!")
                else:
                    log_warning("Port 7860 is still in use, will find alternative...")
            else:
                log_warning("Could not free port 7860, will find alternative...")
        elif choice == "3":
            log_step("Exiting...")
            return False
        # Choice 1 or any other input will find alternative port
    
    # Find available port
    available_port = find_available_port(7860)
    
    if available_port == 7860:
        log_success("Using default port 7860")
    else:
        log_success(f"Using alternative port {available_port}")
    
    # Set environment variable for the app to use
    os.environ['TUBEMATE_PORT'] = str(available_port)
    
    log_step("Starting tubeMate application...")
    
    # Start the application
    try:
        # Import and run the app
        import app
        log_success(f"tubeMate started successfully on port {available_port}!")
        print(f"\n🌐 Access your tubeMate service at:")
        print(f"   http://localhost:{available_port}")
        print(f"   http://0.0.0.0:{available_port}")
        print(f"\n📚 API Documentation available at:")
        print(f"   http://localhost:{available_port}/docs")
        
    except KeyboardInterrupt:
        log_step("Received shutdown signal...")
        log_success("tubeMate stopped gracefully")
    except Exception as e:
        log_error(f"Failed to start tubeMate: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = start_tubeMate()
    sys.exit(0 if success else 1)
