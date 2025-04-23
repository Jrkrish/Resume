#!/usr/bin/env python
"""
Premium Feature Test Runner

This script provides a command-line interface to test the premium features
of the AI Resume Generator application.

Usage:
  python run_premium_tests.py [option]

Options:
  all                 Run all premium feature tests
  variants            Test multiple resume variants
  cover-letter        Test cover letter generation
  ats                 Test ATS optimization
  templates           Test template customization
  unit-tests          Run unit tests for premium features
"""

import sys
import os
import subprocess
import argparse
import time
import webbrowser

def check_server_running():
    """Check if the Flask server is running"""
    import requests
    try:
        response = requests.get("http://localhost:5000")
        return response.status_code == 200
    except:
        return False

def ensure_dependencies():
    """Ensure all required packages are installed"""
    print("Checking dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed.\n")

def run_all_tests():
    """Run all premium feature tests"""
    print("Running all premium feature tests...")
    subprocess.call([sys.executable, "premium_features_demo.py"])

def run_variant_tests():
    """Test multiple resume variants feature"""
    from premium_features_demo import simulate_login_and_payment, test_resume_variants, print_header
    
    print_header("TESTING MULTIPLE RESUME VARIANTS")
    session = simulate_login_and_payment()
    if session:
        test_resume_variants(session)

def run_cover_letter_tests():
    """Test cover letter generation feature"""
    from premium_features_demo import simulate_login_and_payment, test_cover_letter, print_header
    
    print_header("TESTING COVER LETTER GENERATION")
    session = simulate_login_and_payment()
    if session:
        test_cover_letter(session)

def run_ats_tests():
    """Test ATS optimization feature"""
    from premium_features_demo import simulate_login_and_payment, test_ats_optimization, print_header
    
    print_header("TESTING ATS OPTIMIZATION")
    session = simulate_login_and_payment()
    if session:
        test_ats_optimization(session)

def run_template_tests():
    """Test template customization feature"""
    from premium_features_demo import simulate_login_and_payment, test_template_customization, print_header
    
    print_header("TESTING TEMPLATE CUSTOMIZATION")
    session = simulate_login_and_payment()
    if session:
        test_template_customization(session)

def run_unit_tests():
    """Run unit tests for premium features"""
    print("Running unit tests for premium features...")
    subprocess.call([sys.executable, "-m", "unittest", "test_premium_features.py"])

def start_server():
    """Start the Flask server if not already running"""
    if not check_server_running():
        print("Starting Flask server...")
        # Start the server in a subprocess
        server_process = subprocess.Popen([sys.executable, "app.py"])
        
        # Wait for the server to start
        print("Waiting for server to start...")
        max_attempts = 10
        for attempt in range(max_attempts):
            if check_server_running():
                print("Server is up and running!")
                return server_process
            print(f"Attempt {attempt+1}/{max_attempts}...")
            time.sleep(1)
        
        print("Failed to start server.")
        return None
    else:
        print("Server is already running.")
        return None

def main():
    parser = argparse.ArgumentParser(description='Test premium features of the AI Resume Generator')
    parser.add_argument('test', choices=['all', 'variants', 'cover-letter', 'ats', 'templates', 'unit-tests'], 
                        help='Which premium feature to test')
    
    args = parser.parse_args()
    
    # Ensure dependencies are installed
    ensure_dependencies()
    
    # Start the server if needed
    server_process = None
    if args.test != 'unit-tests':  # Unit tests don't need the server
        server_process = start_server()
    
    try:
        # Run the selected test
        if args.test == 'all':
            run_all_tests()
        elif args.test == 'variants':
            run_variant_tests()
        elif args.test == 'cover-letter':
            run_cover_letter_tests()
        elif args.test == 'ats':
            run_ats_tests()
        elif args.test == 'templates':
            run_template_tests()
        elif args.test == 'unit-tests':
            run_unit_tests()
    finally:
        # Stop the server if we started it
        if server_process:
            print("Stopping server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, show help
        print(__doc__)
    else:
        main() 