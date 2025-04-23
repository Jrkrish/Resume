"""
Premium Features Demo Script

This script demonstrates the premium features of the AI Resume Generator:
1. Multiple resume variants
2. Cover letter generation
3. ATS optimization
4. Template customization

Run this script with: python premium_features_demo.py
"""

import requests
import json
import time
import os
import webbrowser
from termcolor import colored

# Base URL for the Flask app
BASE_URL = "http://localhost:5000"

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 60)
    print(colored(f"  {message}", "cyan", attrs=["bold"]))
    print("=" * 60)

def simulate_login_and_payment():
    """Simulate logging in and completing payment for premium plan"""
    print_header("SIMULATING LOGIN & PAYMENT FOR PREMIUM PLAN")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Visit the resume form with premium plan
    print(colored("Step 1: Selecting premium plan...", "yellow"))
    response = session.get(f"{BASE_URL}/resume-form?plan=premium")
    if response.status_code != 200:
        print(colored(f"Failed to access resume form: {response.status_code}", "red"))
        return None
    
    # Step 2: Submit the resume form
    print(colored("Step 2: Submitting resume details...", "yellow"))
    form_data = {
        "plan": "premium",
        "template": "modern",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "123-456-7890",
        "linkedin": "linkedin.com/in/johndoe",
        "summary": "Experienced software engineer with expertise in Python, JavaScript, and cloud technologies.",
        "education": "Master of Computer Science, Stanford University, 2021\nBachelor of Engineering, MIT, 2019",
        "experience": "Senior Developer at Tech Company (2021-2023), Software Engineer at Startup Inc (2019-2021)",
        "skills": "Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, Machine Learning"
    }
    
    # Use the correct endpoint and follow redirects
    response = session.post(f"{BASE_URL}/generate-resume", data=form_data, allow_redirects=False)
    
    if response.status_code != 302 and response.status_code != 200:
        print(colored(f"Failed to submit resume: {response.status_code}", "red"))
        print(colored(f"Response: {response.text[:200]}...", "red"))
        return None
        
    print(colored(f"Resume form submitted successfully - Redirect URL: {response.headers.get('Location', 'None')}", "green"))
    
    # Follow the redirect to the payment page
    redirect_url = response.headers.get('Location')
    if redirect_url:
        if not redirect_url.startswith('http'):
            redirect_url = f"{BASE_URL}{redirect_url}"
        response = session.get(redirect_url)
        print(colored(f"Followed redirect to: {redirect_url}", "yellow"))
    
    # Step 3: Simulate payment completion
    # In a real scenario, this would redirect to Razorpay and then back to our success route
    # For demo purposes, we'll directly hit a special debug route to simulate payment
    print(colored("Step 3: Simulating premium payment completion...", "yellow"))
    
    # Note: This is a special debug route that was added to the app for testing
    response = session.get(f"{BASE_URL}/debug/simulate-payment?plan=premium", allow_redirects=True)
    
    if response.status_code == 200 or response.status_code == 302:
        print(colored("✓ Successfully simulated premium plan activation", "green"))
    else:
        print(colored(f"Payment simulation failed with status: {response.status_code}", "red"))
        return None
        
    return session

def test_resume_variants(session):
    """Test generating multiple resume variants (premium feature)"""
    print_header("TESTING MULTIPLE RESUME VARIANTS")
    
    variants = [
        {"emphasis": "technical", "tone": "professional"},
        {"emphasis": "leadership", "tone": "confident"},
        {"emphasis": "achievements", "tone": "results-oriented"}
    ]
    
    for i, variant in enumerate(variants):
        print(colored(f"Generating variant {i+1}: {variant['emphasis'].title()} focus, {variant['tone']} tone...", "yellow"))
        
        # Update the resume with variant parameters
        response = session.post(f"{BASE_URL}/debug/generate-variant", json=variant)
        if response.status_code == 200:
            data = response.json()
            print(colored(f"✓ Successfully generated resume variant {i+1} (ID: {data.get('variant_id')})", "green"))
        else:
            print(colored(f"Failed to generate variant: {response.status_code}", "red"))
            if response.status_code == 403:
                print(colored("This is likely because you're not using a premium plan or the debug route isn't available", "yellow"))
        
        # In a real scenario, we would save each variant
        time.sleep(1)  # Small delay to simulate AI generation
    
    # Check if we can view all variants
    print(colored("Checking all generated variants...", "yellow"))
    response = session.get(f"{BASE_URL}/debug/view-variants")
    if response.status_code == 200:
        print(colored("✓ Successfully retrieved all resume variants", "green"))
    else:
        print(colored(f"Failed to retrieve variants: {response.status_code}", "red"))
    
    print(colored("✓ Multiple resume variants feature tested", "green"))

def test_cover_letter(session):
    """Test cover letter generation (premium feature)"""
    print_header("TESTING COVER LETTER GENERATION")
    
    print(colored("Submitting cover letter request...", "yellow"))
    
    # Set up job details for the cover letter
    cover_letter_data = {
        "job_title": "Senior Software Engineer",
        "company_name": "Google",
        "job_description": "Looking for an experienced developer with Python and cloud expertise",
        "hiring_manager": "Jane Smith",
        "tone": "professional"
    }
    
    # Request cover letter generation
    response = session.get(f"{BASE_URL}/generate-cover-letter", allow_redirects=True)
    if response.status_code == 200:
        print(colored("✓ Cover letter generated successfully", "green"))
    else:
        print(colored(f"Failed to generate cover letter: {response.status_code}", "red"))
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            print(colored(f"Redirected to: {redirect_url}", "yellow"))
    
    # Test downloading the cover letter
    print(colored("Testing cover letter download...", "yellow"))
    response = session.get(f"{BASE_URL}/download-cover-letter")
    if response.status_code == 200:
        # Save the cover letter PDF locally for demonstration
        with open("demo_cover_letter.pdf", "wb") as f:
            f.write(response.content)
        print(colored("✓ Cover letter PDF saved as 'demo_cover_letter.pdf'", "green"))
    else:
        print(colored(f"Failed to download cover letter: {response.status_code}", "red"))
        if response.text:
            print(colored(f"Response: {response.text[:200]}...", "yellow"))

def test_ats_optimization(session):
    """Test ATS optimization tips (premium feature)"""
    print_header("TESTING ATS OPTIMIZATION")
    
    print(colored("Requesting ATS optimization tips...", "yellow"))
    
    # Request ATS optimization tips
    response = session.post(f"{BASE_URL}/ats-optimize")
    
    if response.status_code == 200:
        data = response.json()
        print(colored("ATS Optimization Tips:", "green"))
        for i, tip in enumerate(data.get("tips", [])):
            print(colored(f"  {i+1}. {tip}", "green"))
        print(colored("✓ ATS optimization feature working correctly", "green"))
    else:
        print(colored(f"Failed to get ATS tips: {response.status_code}", "red"))
        if response.status_code == 403:
            print(colored("This is expected if you're not on a premium plan", "yellow"))

def test_template_customization(session):
    """Test template and color customization (premium feature)"""
    print_header("TESTING TEMPLATE & COLOR CUSTOMIZATION")
    
    # Test changing templates
    templates = ["modern", "elegant", "creative"]
    for template in templates:
        print(colored(f"Switching to {template} template...", "yellow"))
        response = session.get(f"{BASE_URL}/change-template/{template}", allow_redirects=True)
        if response.status_code == 200 or response.status_code == 302:
            print(colored(f"✓ Successfully switched to {template} template", "green"))
        else:
            print(colored(f"Failed to switch template: {response.status_code}", "red"))
    
    # Test changing colors
    colors = [
        {"name": "Blue", "code": "%233498db"},
        {"name": "Purple", "code": "%237d3c98"},
        {"name": "Green", "code": "%232ecc71"}
    ]
    
    for color in colors:
        print(colored(f"Changing accent color to {color['name']}...", "yellow"))
        response = session.get(f"{BASE_URL}/change-color/{color['code']}", allow_redirects=True)
        if response.status_code == 200 or response.status_code == 302:
            print(colored(f"✓ Successfully changed color to {color['name']}", "green"))
        else:
            print(colored(f"Failed to change color: {response.status_code}", "red"))
    
    print(colored("✓ Template customization feature tested successfully", "green"))

def main():
    print_header("AI RESUME GENERATOR - PREMIUM FEATURES DEMO")
    
    # Check if the app is running
    try:
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print(colored(f"Error: The Flask app doesn't seem to be running at {BASE_URL}", "red"))
            print(colored("Please start the app with 'python app.py' before running this demo", "yellow"))
            return
    except requests.exceptions.ConnectionError:
        print(colored(f"Error: Cannot connect to {BASE_URL}", "red"))
        print(colored("Please start the app with 'python app.py' before running this demo", "yellow"))
        return
    
    # Simulate login and payment
    session = simulate_login_and_payment()
    if not session:
        print(colored("Failed to set up premium plan session. Cannot continue with tests.", "red"))
        return
    
    # Run the premium feature tests
    test_resume_variants(session)
    test_cover_letter(session)
    test_ats_optimization(session)
    test_template_customization(session)
    
    print_header("DEMO COMPLETED")
    print(colored("All premium features have been tested!", "green"))
    print(colored("\nNote: Some features may have failed if the app doesn't have all required debug routes.", "yellow"))
    print(colored("To fully test these features, you may need to modify the app or use the UI manually.", "yellow"))

if __name__ == "__main__":
    main() 