@echo off
REM Script to run the QiLifeStore Social Media Engagement Bot on Windows

REM Change to the project root directory
cd %~dp0..

REM Check for Python virtual environment
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the bot with provided arguments
python run.py %*

REM Check the exit code
if %ERRORLEVEL% EQU 0 (
    echo Bot execution completed successfully.
) else (
    echo Bot execution failed. Check logs for details.
)

REM Pause so the window doesn't close immediately
pause 