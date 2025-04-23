#!/usr/bin/env python
"""
Environment Setup Script for Premium Features Testing

This script ensures the correct environment is set up for testing premium features
by installing compatible package versions and resolving dependency conflicts.
"""

import subprocess
import sys
import os
import importlib.metadata

def install_dependencies():
    """Install the correct versions of dependencies"""
    print("Installing dependencies with compatible versions...")
    
    # First, uninstall problematic packages
    subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", 
                    "Flask", "Werkzeug", "flask-debugtoolbar"])
    
    # Install packages in the correct order with specific versions that work together
    dependencies = [
        "Werkzeug==2.2.3",
        "Flask==2.2.3",
        "flask-debugtoolbar==0.13.1",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "termcolor==2.2.0",
        "google-generativeai==0.3.1",
        "pdfkit==1.0.0",
        "razorpay==1.3.0"
    ]
    
    for dependency in dependencies:
        print(f"Installing {dependency}...")
        subprocess.call([sys.executable, "-m", "pip", "install", dependency])
    
    print("Dependencies installed successfully!")

def check_installation():
    """Check if the installation was successful"""
    try:
        # Use importlib.metadata to safely check versions
        try:
            flask_version = importlib.metadata.version("flask")
            werkzeug_version = importlib.metadata.version("werkzeug")
            flask_debugtoolbar_version = importlib.metadata.version("flask-debugtoolbar")
            
            print(f"Flask version: {flask_version}")
            print(f"Werkzeug version: {werkzeug_version}")
            print(f"Flask-DebugToolbar version: {flask_debugtoolbar_version}")
        except importlib.metadata.PackageNotFoundError as e:
            print(f"Package not found: {e}")
            return False
            
        # Verify other required packages
        import requests
        import termcolor
        import google.generativeai
        import pdfkit
        import razorpay
        
        print("All required packages are installed!")
        return True
    except ImportError as e:
        print(f"Error: {e}")
        return False

def fix_tests():
    """Update test files to be compatible with Flask 2.2.3"""
    files_to_update = [
        "premium_features_demo.py",
        "test_premium_features.py",
        "app.py"
    ]
    
    for file in files_to_update:
        if os.path.exists(file):
            print(f"Updating {file} to be compatible with Flask 2.2.3...")
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update session transaction method if needed
            if "session_transaction" in content and file == "test_premium_features.py":
                content = content.replace("sess['form_data']", "sess['resume_data']")
                content = content.replace("sess['plan']", "sess['selected_plan']")
            
            # Update debug route in app.py
            if file == "app.py" and "@app.route('/debug/simulate-payment')" in content:
                print("  Updating debug/simulate-payment route in app.py")
                
                # Make sure to use selected_plan and payment_successful
                if "session['plan'] = plan" in content:
                    content = content.replace("session['plan'] = plan", 
                                             "session['selected_plan'] = plan")
                
                if "session['payment_completed'] = True" in content:
                    content = content.replace("session['payment_completed'] = True", 
                                             "session['payment_successful'] = True")
            
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)

def main():
    print("Setting up environment for premium features testing...")
    
    # Install dependencies with stable versions
    install_dependencies()
    
    # Check installation
    if check_installation():
        # Fix test files for compatibility
        fix_tests()
        
        print("\nEnvironment setup complete! You can now run the premium features tests:")
        print("  python run_premium_tests.py all")
    else:
        print("\nEnvironment setup failed. Please check the errors above.")

if __name__ == "__main__":
    main() 