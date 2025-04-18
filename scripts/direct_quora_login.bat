@echo off
echo ====================================================
echo Direct Quora Login Script 
echo ====================================================
echo This script uses multiple approaches to log into Quora:
echo - Approach 1: XPath selectors
echo - Approach 2: CSS attribute selectors
echo - Approach 3: Input indexes and Enter key
echo - Approach 4: JavaScript DOM manipulation
echo.
echo Detailed logs and screenshots will be saved to the logs directory.
echo ====================================================
echo.

echo Installing required packages...
pip install selenium
pip install undetected-chromedriver -U
echo.

echo Clearing previous ChromeDriver installations...
if exist "%USERPROFILE%\.wdm\drivers\chromedriver" (
    rmdir /s /q "%USERPROFILE%\.wdm\drivers\chromedriver"
    echo ChromeDriver cache cleared.
)
echo.

echo Running Quora login script...
python "%~dp0\direct_quora_login.py"

echo.
echo Check logs/direct_quora_login.log for detailed information
pause 