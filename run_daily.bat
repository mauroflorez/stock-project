@echo off
REM ================================================================
REM  Stock Investment Planner - Daily Run Script
REM  Use this with Windows Task Scheduler for automated daily runs
REM ================================================================

echo ================================================================
echo  Stock Investment Planner - Daily Run
echo  %date% %time%
echo ================================================================

REM Set the project directory (update if your project is in a different location)
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Step 1: Make sure Ollama is running
echo.
echo Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama...
    start /min "" "ollama" serve
    timeout /t 10 /nobreak >nul
)

REM Step 2: Run the main analysis
echo.
echo Step 1/2: Running stock analysis...
python main.py
if %errorlevel% neq 0 (
    echo ERROR: Stock analysis failed!
    pause
    exit /b 1
)

REM Step 3: Generate HTML reports
echo.
echo Step 2/2: Generating HTML reports...
python generate_report.py
if %errorlevel% neq 0 (
    echo ERROR: Report generation failed!
    pause
    exit /b 1
)

echo.
echo ================================================================
echo  All done! Reports updated successfully.
echo  %date% %time%
echo ================================================================

REM Optional: auto-commit and push to GitHub
REM Uncomment the lines below if you want automatic deployment
REM git add docs/
REM git commit -m "Daily stock analysis update - %date%"
REM git push
