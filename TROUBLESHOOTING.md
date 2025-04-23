# Troubleshooting Premium Features Testing

This guide covers common issues that may occur when testing premium features and provides solutions.

## Installation and Dependency Issues

### Problem: Flask Import Error After Setup

```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
1. Reset your environment with the stable versions:
   ```
   python setup_environment.py
   ```
2. If that fails, try manually installing Flask:
   ```
   pip install Flask==2.2.3 Werkzeug==2.2.3 flask-debugtoolbar==0.13.1
   ```
3. Check if it's available:
   ```
   python -c "import flask; print('Flask is available')"
   ```

### Problem: Werkzeug or Other Package Version Conflicts

**Solution:**
1. Use the requirements.backup.txt file created by the test script:
   ```
   pip install -r requirements.backup.txt
   ```

## Flask App Startup Issues

### Problem: Server Fails to Start

**Solution:**
1. Check for syntax errors in app.py
2. Look for import errors in the console output
3. Make sure DEBUG=True in app.py
4. Ensure port 5000 is not in use by another application

### Problem: Debug Routes Not Working

**Solution:**
1. Verify debug mode is enabled in app.py:
   ```python
   app.debug = True
   ```
2. Check that the routes are properly defined:
   ```python
   @app.route('/debug/simulate-payment')
   def debug_simulate_payment():
       ...
   ```
3. Ensure you're accessing them correctly from the test scripts

## Session Management Issues

### Problem: Session Variables Not Persistent

**Solution:**
1. Check session key names (should be `selected_plan`, `resume_data`, `payment_successful`)
2. Ensure the app's secret key is set:
   ```python
   app.secret_key = 'your-secret-key'  # Or from environment variable
   ```
3. Verify your browser accepts cookies for localhost

### Problem: Session Values Not Being Set

**Solution:**
1. Print session contents for debugging:
   ```python
   print(dict(session))
   ```
2. Check session is being modified in the correct route
3. Ensure redirect after session updates

## Test Script Issues

### Problem: Tests Fail at Form Submission

**Solution:**
1. Ensure all required form fields are included:
   ```python
   form_data = {
       "plan": "premium",
       "template": "modern",  # Often missing
       "name": "Test User",
       # Other fields...
   }
   ```

2. Use `allow_redirects=False` for proper redirect handling
3. Add more error reporting to debug the issue:
   ```python
   print(response.text)  # Print server response
   ```

### Problem: ATS Optimization Tests Fail

**Solution:**
1. Verify the `/ats-optimize` route exists in app.py
2. Make sure the premium plan is set in the session
3. Check that mock responses are set up properly in unit tests

## API Keys and External Services

### Problem: Gemini AI API Calls Fail

**Solution:**
1. Check your .env file contains a valid GEMINI_API_KEY
2. Verify the API key is being loaded correctly
3. Consider mocking these calls for testing:
   ```python
   @patch('app.model.generate_content')
   def test_function(self, mock_generate):
       mock_response = MagicMock()
       mock_response.text = 'Mocked response'
       mock_generate.return_value = mock_response
       # Test code
   ```

### Problem: Razorpay Integration Issues

**Solution:**
1. For testing, use the debug route instead of actual Razorpay calls
2. Set debug Razorpay keys in your .env file
3. Mock Razorpay responses in unit tests

## PDF Generation Issues

### Problem: PDF Generation Fails

**Solution:**
1. Ensure wkhtmltopdf is installed on your system
2. Check the path to wkhtmltopdf is correct
3. For testing, you can mock the PDF generation:
   ```python
   @patch('pdfkit.from_string')
   def test_download(self, mock_pdf):
       mock_pdf.return_value = b'PDF content'
       # Test code
   ```

## When All Else Fails

If you're still having issues:

1. Restore from backup:
   ```
   cp requirements.backup.txt requirements.txt
   pip install -r requirements.txt
   ```

2. Reset your virtual environment (if using one):
   ```
   deactivate  # If using venv
   python -m venv venv --clear  # Create fresh environment
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. Check for Python version compatibility issues (requires Python 3.7+)

4. Look at the Flask application logs for detailed error messages 