#!/usr/bin/env python3
"""
Test script to verify the port finding functionality works correctly.
"""

import socket
import time
import threading
from logging_config import setup_logging, log_step, log_success, log_error

def find_available_port(start_port=7860, max_attempts=100):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                log_success(f"Found available port: {port}")
                return port
        except OSError:
            continue
    
    # If no port found in range, try system-assigned port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 0))
        port = s.getsockname()[1]
        log_success(f"Using system-assigned port: {port}")
        return port

def occupy_port(port, duration=5):
    """Occupy a port for testing purposes"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            s.listen(1)
            log_step(f"Occupying port {port} for {duration} seconds...")
            time.sleep(duration)
            log_step(f"Released port {port}")
    except OSError as e:
        log_error(f"Could not occupy port {port}: {e}")

def test_port_finder():
    """Test the port finding functionality"""
    setup_logging()
    
    print("🧪 Testing Port Finder Functionality")
    print("=" * 50)
    
    # Test 1: Find port when 7860 is available
    log_step("Test 1: Finding port when 7860 is available")
    port1 = find_available_port(7860)
    print(f"✅ Found port: {port1}")
    
    # Test 2: Find port when 7860 is occupied
    log_step("Test 2: Finding port when 7860 is occupied")
    
    # Start a thread to occupy port 7860
    occupy_thread = threading.Thread(target=occupy_port, args=(7860, 3), daemon=True)
    occupy_thread.start()
    
    # Give it a moment to bind
    time.sleep(0.5)
    
    # Now try to find an available port
    port2 = find_available_port(7860)
    print(f"✅ Found alternative port: {port2}")
    
    # Test 3: Multiple port finding
    log_step("Test 3: Finding multiple ports simultaneously")
    ports = []
    for i in range(3):
        port = find_available_port(7860 + i * 10)
        ports.append(port)
        print(f"✅ Found port {i+1}: {port}")
    
    print("\n" + "=" * 50)
    print("🎉 All port finder tests completed successfully!")
    print(f"📊 Ports found: {ports}")
    
    return True

if __name__ == "__main__":
    test_port_finder()
