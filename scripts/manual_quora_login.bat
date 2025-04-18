@echo off
echo ====================================================
echo Simplified Manual Quora Login Script
echo ====================================================
echo This is a simplified script designed to work on Windows
echo systems with Chrome installed. It avoids using ChromeDriver
echo manager which may cause compatibility issues.
echo.
echo Requirements:
echo - Chrome browser installed
echo - Selenium Python package
echo ====================================================
echo.

echo Installing Selenium...
pip install selenium
echo.

echo Running simplified login script...
python "%~dp0\manual_quora_login.py"

echo.
echo Script completed.
pause 