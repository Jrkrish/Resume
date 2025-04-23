@echo off
echo ===================================================
echo     AI Resume Generator Premium Features Test
echo ===================================================
echo.

REM Set up the environment
echo Setting up environment...
python setup_environment.py
if %ERRORLEVEL% NEQ 0 (
    echo Environment setup failed. Please check the errors above.
    pause
    exit /b 1
)

REM Create a backup of the current requirements.txt file
echo Creating backup of requirements.txt...
copy requirements.txt requirements.backup.txt

REM Check if Flask app can start
echo Checking if Flask app can start...
python -c "import flask; print('Flask is available')"
if %ERRORLEVEL% NEQ 0 (
    echo Flask import failed! Rolling back to backup requirements...
    copy requirements.backup.txt requirements.txt
    pip install -r requirements.txt
    echo Please try running the setup script manually: python setup_environment.py
    pause
    exit /b 1
)

echo Starting Flask app for testing...
start cmd /k "python app.py"

REM Wait for the server to start
echo Waiting for server to start...
timeout /t 5 /nobreak

REM Verify server is running
python -c "import requests; exit(0 if requests.get('http://localhost:5000').status_code == 200 else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo Server failed to start! Please check the server console window for errors.
    timeout /t 5 /nobreak
    exit /b 1
)

echo.
echo Running premium features tests...
python run_premium_tests.py all

echo.
echo Test completed! Press any key to exit.
pause > nul 