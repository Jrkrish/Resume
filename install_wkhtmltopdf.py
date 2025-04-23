#!/usr/bin/env python3
"""
Installation script for wkhtmltopdf.
This script will download and install wkhtmltopdf and update the wkhtmltopdf_config.py file.
"""
import os
import platform
import subprocess
import sys
import tempfile
import urllib.request
import shutil
from pathlib import Path

# Define download URLs for different platforms
DOWNLOADS = {
    "Windows": {
        "64bit": "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe",
        "32bit": "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win32.exe"
    },
    "Darwin": {  # macOS
        "64bit": "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.macos-cocoa.pkg"
    },
    "Linux": {
        "64bit-deb": "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb",
        "64bit-rpm": "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.centos8.x86_64.rpm"
    }
}

def detect_system():
    """Detect the operating system and architecture."""
    system = platform.system()
    machine = platform.machine().lower()
    
    if system == "Windows":
        arch = "64bit" if platform.architecture()[0] == "64bit" else "32bit"
        return system, arch
    
    elif system == "Darwin":  # macOS
        return system, "64bit"
    
    elif system == "Linux":
        if os.path.exists("/etc/debian_version") or os.path.exists("/etc/ubuntu_version"):
            return "Linux", "64bit-deb"
        elif os.path.exists("/etc/redhat-release") or os.path.exists("/etc/fedora-release"):
            return "Linux", "64bit-rpm"
        else:
            return "Linux", "unknown"
    
    return system, "unknown"

def download_wkhtmltopdf(url, target_path):
    """Download wkhtmltopdf installer from the given URL."""
    print(f"Downloading wkhtmltopdf from {url}...")
    try:
        urllib.request.urlretrieve(url, target_path)
        print(f"Downloaded to {target_path}")
        return True
    except Exception as e:
        print(f"Failed to download: {e}")
        return False

def install_wkhtmltopdf(installer_path, system):
    """Install wkhtmltopdf based on the operating system."""
    print("Installing wkhtmltopdf...")
    
    try:
        if system == "Windows":
            print("Running installer... Please follow the installation wizard.")
            print("IMPORTANT: Note the installation directory for later configuration.")
            subprocess.run([installer_path], check=True)
            
        elif system == "Darwin":  # macOS
            print("Running installer... You may be prompted for your password.")
            subprocess.run(["sudo", "installer", "-pkg", installer_path, "-target", "/"], check=True)
            
        elif system == "Linux":
            if installer_path.endswith(".deb"):
                print("Installing DEB package... You may be prompted for your password.")
                subprocess.run(["sudo", "dpkg", "-i", installer_path], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-f", "-y"], check=True)  # Fix dependencies
            elif installer_path.endswith(".rpm"):
                print("Installing RPM package... You may be prompted for your password.")
                subprocess.run(["sudo", "rpm", "-i", installer_path], check=True)
            
        print("Installation completed!")
        return True
        
    except Exception as e:
        print(f"Installation failed: {e}")
        return False

def locate_wkhtmltopdf():
    """Try to locate wkhtmltopdf executable after installation."""
    system = platform.system()
    
    if system == "Windows":
        paths = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe"
        ]
    elif system == "Darwin":  # macOS
        paths = [
            "/usr/local/bin/wkhtmltopdf",
            "/opt/homebrew/bin/wkhtmltopdf"
        ]
    else:  # Linux
        paths = [
            "/usr/bin/wkhtmltopdf",
            "/usr/local/bin/wkhtmltopdf"
        ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    # If not found in standard locations, try a basic command search
    try:
        if system == "Windows":
            result = subprocess.run(["where", "wkhtmltopdf"], capture_output=True, text=True, check=False)
        else:
            result = subprocess.run(["which", "wkhtmltopdf"], capture_output=True, text=True, check=False)
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")[0]
    except Exception:
        pass
    
    return None

def update_config(wkhtmltopdf_path):
    """Update the wkhtmltopdf_config.py file with the correct path."""
    if not wkhtmltopdf_path:
        print("WARNING: Could not locate wkhtmltopdf executable.")
        print("You may need to manually update the wkhtmltopdf_config.py file.")
        return False
    
    config_path = Path(__file__).parent / "wkhtmltopdf_config.py"
    content = f'''"""
Configuration file for wkhtmltopdf path.
This file is generated by the install_wkhtmltopdf.py script.
You can manually edit this file if the path to wkhtmltopdf changes.
"""

# Path to wkhtmltopdf executable
WKHTMLTOPDF_PATH = r"{wkhtmltopdf_path}"
'''
    
    try:
        with open(config_path, "w") as f:
            f.write(content)
        print(f"Updated configuration file: {config_path}")
        print(f"wkhtmltopdf path set to: {wkhtmltopdf_path}")
        return True
    except Exception as e:
        print(f"Failed to update configuration file: {e}")
        return False

def test_wkhtmltopdf(wkhtmltopdf_path):
    """Test if wkhtmltopdf is working correctly."""
    if not wkhtmltopdf_path:
        return False
    
    print("Testing wkhtmltopdf installation...")
    test_html = "<html><body><h1>Test PDF Generation</h1><p>This is a test.</p></body></html>"
    test_html_path = os.path.join(tempfile.gettempdir(), "test.html")
    test_pdf_path = os.path.join(tempfile.gettempdir(), "test.pdf")
    
    try:
        with open(test_html_path, "w") as f:
            f.write(test_html)
        
        subprocess.run([wkhtmltopdf_path, test_html_path, test_pdf_path], check=True)
        
        if os.path.exists(test_pdf_path) and os.path.getsize(test_pdf_path) > 0:
            print("wkhtmltopdf is working correctly!")
            return True
        else:
            print("Test PDF generation failed.")
            return False
    except Exception as e:
        print(f"wkhtmltopdf test failed: {e}")
        return False
    finally:
        # Clean up test files
        for path in [test_html_path, test_pdf_path]:
            if os.path.exists(path):
                os.remove(path)

def manual_install_instructions():
    """Display manual installation instructions."""
    system = platform.system()
    
    print("\n--- Manual Installation Instructions ---")
    print("If the automatic installation failed, you can install wkhtmltopdf manually:")
    
    if system == "Windows":
        print("1. Download wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html")
        print("2. Run the installer and follow the instructions")
        print("3. Open wkhtmltopdf_config.py in a text editor")
        print("4. Update the WKHTMLTOPDF_PATH variable with the path to wkhtmltopdf.exe")
        print("   (typically C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe)")
    
    elif system == "Darwin":  # macOS
        print("1. Install with Homebrew: brew install wkhtmltopdf")
        print("   OR download from: https://wkhtmltopdf.org/downloads.html")
        print("2. Install the package")
        print("3. Open wkhtmltopdf_config.py in a text editor")
        print("4. Update the WKHTMLTOPDF_PATH variable with the path to wkhtmltopdf")
        print("   (typically /usr/local/bin/wkhtmltopdf)")
    
    else:  # Linux
        print("1. Use your package manager:")
        print("   - Debian/Ubuntu: sudo apt-get install wkhtmltopdf")
        print("   - RHEL/CentOS: sudo yum install wkhtmltopdf")
        print("   OR download from: https://wkhtmltopdf.org/downloads.html")
        print("2. Open wkhtmltopdf_config.py in a text editor")
        print("3. Update the WKHTMLTOPDF_PATH variable with the path to wkhtmltopdf")
        print("   (typically /usr/bin/wkhtmltopdf)")

def main():
    """Main function to run the installation."""
    print("=== wkhtmltopdf Installer ===")
    
    # Detect system
    system, arch = detect_system()
    print(f"Detected system: {system} {arch}")
    
    # Check if wkhtmltopdf is already installed
    existing_path = locate_wkhtmltopdf()
    if existing_path:
        print(f"wkhtmltopdf is already installed at: {existing_path}")
        if test_wkhtmltopdf(existing_path):
            update_config(existing_path)
            print("Installation successful. You're ready to generate PDFs!")
            return True
        else:
            print("Existing installation seems to be broken. Trying to reinstall...")
    
    # Get download URL
    if system not in DOWNLOADS or arch not in DOWNLOADS[system]:
        print(f"Sorry, automatic installation is not supported for {system} {arch}.")
        manual_install_instructions()
        return False
    
    download_url = DOWNLOADS[system][arch]
    
    # Create temp directory for the installer
    with tempfile.TemporaryDirectory() as temp_dir:
        # Build the installer path
        installer_filename = os.path.basename(download_url)
        installer_path = os.path.join(temp_dir, installer_filename)
        
        # Download the installer
        if not download_wkhtmltopdf(download_url, installer_path):
            manual_install_instructions()
            return False
        
        # Install wkhtmltopdf
        if not install_wkhtmltopdf(installer_path, system):
            manual_install_instructions()
            return False
    
    # Locate wkhtmltopdf after installation
    wkhtmltopdf_path = locate_wkhtmltopdf()
    
    # Update configuration
    update_config(wkhtmltopdf_path)
    
    # Test the installation
    if test_wkhtmltopdf(wkhtmltopdf_path):
        print("Installation successful. You're ready to generate PDFs!")
        return True
    else:
        manual_install_instructions()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 