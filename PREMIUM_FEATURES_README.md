# Premium Features Testing

This directory contains scripts to test and demonstrate the premium features of the AI Resume Generator.

## Available Premium Features

1. **Multiple Resume Variants** - Create up to 3 different versions of your resume with different emphasis (technical, leadership, achievements) and tone (professional, confident, results-oriented).

2. **Cover Letter Generation** - Automatically generate a cover letter that matches your resume and is tailored to a specific job position.

3. **ATS Optimization** - Get specific tips on how to improve your resume to pass Applicant Tracking Systems.

4. **Template Customization** - Access all templates and color customization options.

## How to Test Premium Features

### Prerequisites

- Python 3.7+
- pip (Python package installer)
- All packages listed in requirements.txt

### Quick Start

The easiest way to run the tests is using our automated test scripts:

**Windows:**
```
test_premium_features.bat
```

**Linux/Mac:**
```
chmod +x test_premium_features.sh
./test_premium_features.sh
```

These scripts will:
1. Set up the correct environment
2. Start the Flask app
3. Run all premium features tests
4. Display the results

### Manual Installation

If you prefer to run the tests manually:

1. Install required dependencies and set up the environment:
   ```
   python setup_environment.py
   ```

2. Make sure your Flask app is running:
   ```
   python app.py
   ```

3. In a separate terminal, run the premium features tests.

### Running the Tests

You can use the `run_premium_tests.py` script to test various premium features:

```
# Run all premium feature tests
python run_premium_tests.py all

# Test only multiple resume variants
python run_premium_tests.py variants

# Test only cover letter generation
python run_premium_tests.py cover-letter

# Test only ATS optimization
python run_premium_tests.py ats

# Test only template customization
python run_premium_tests.py templates

# Run unit tests for premium features
python run_premium_tests.py unit-tests
```

Alternatively, you can run the demo script directly:

```
python premium_features_demo.py
```

### Understanding the Test Results

The test scripts will:

1. Simulate logging in with a premium plan
2. Simulate payment completion
3. Test each premium feature
4. Show the results in the terminal

## Debug Routes

For testing purposes, the following debug routes have been added to the Flask app:

- `/debug/simulate-payment?plan=premium` - Simulates completing payment for a premium plan
- `/debug/generate-variant` - Generates a resume variant with specific parameters
- `/debug/view-variants` - View all generated resume variants

These routes are only available when the app is running in debug mode.

## Manual Testing

You can also test the premium features manually through the web interface:

1. Start the Flask app: `python app.py`
2. Visit `http://localhost:5000` in your browser
3. Fill out the resume form with your information
4. Select the "Premium" plan
5. Use the simulated payment flow (with Razorpay in test mode)
6. Test features through the UI

## Troubleshooting

If you encounter issues:

1. **Dependency Conflicts**: Use the `setup_environment.py` script to resolve package version conflicts
   ```
   python setup_environment.py
   ```

2. **Session Key Errors**: The test scripts expect specific session key names used in app.py:
   - `selected_plan` (not `plan`)
   - `resume_data` (not `form_data`)
   - `payment_successful` (not `payment_completed`)

3. **Debug Routes Not Working**: Ensure the app is running in debug mode:
   ```python
   app.debug = True
   ```

4. **Form Submission Failures**: Make sure you're providing all required fields, including `template`

5. **Redirects Not Working**: Use `allow_redirects=True` in your requests.Session() calls

## Notes for Developers

- The test scripts use the requests library to interact with the Flask app's API
- Unit tests use the unittest framework with mocking to simulate the AI responses
- Debug routes are provided to bypass normal authentication and payment flows for testing 