#!/bin/bash

echo "==================================================="
echo "    AI Resume Generator Premium Features Test"
echo "==================================================="
echo

# Set up the environment
echo "Setting up environment..."
python setup_environment.py
if [ $? -ne 0 ]; then
    echo "Environment setup failed. Please check the errors above."
    exit 1
fi

# Create a backup of the current requirements.txt file
echo "Creating backup of requirements.txt..."
cp requirements.txt requirements.backup.txt

# Check if Flask app can start
echo "Checking if Flask app can start..."
python -c "import flask; print('Flask is available')"
if [ $? -ne 0 ]; then
    echo "Flask import failed! Rolling back to backup requirements..."
    cp requirements.backup.txt requirements.txt
    pip install -r requirements.txt
    echo "Please try running the setup script manually: python setup_environment.py"
    exit 1
fi

echo
echo "Starting Flask app for testing..."
python app.py &
APP_PID=$!

# Wait for the server to start
echo "Waiting for server to start..."
sleep 5

# Verify server is running
python -c "import requests; exit(0 if requests.get('http://localhost:5000').status_code == 200 else 1)"
if [ $? -ne 0 ]; then
    echo "Server failed to start! Killing process..."
    kill $APP_PID 2>/dev/null
    echo "Please check the app logs for errors."
    exit 1
fi

echo
echo "Running premium features tests..."
python run_premium_tests.py all

echo
echo "Tests completed! Shutting down Flask app..."
kill $APP_PID 2>/dev/null

echo
echo "Done!" 