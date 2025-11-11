@echo off
REM Activate virtual environment and run the connector

call venv\Scripts\activate

if "%1"=="" (
    echo Usage: run.bat [check^|discover^|read]
    echo.
    echo Examples:
    echo   run.bat check
    echo   run.bat discover
    echo   run.bat read
    exit /b 1
)

if "%1"=="check" (
    python main.py check --config secrets\config.json
) else if "%1"=="discover" (
    python main.py discover --config secrets\config.json
) else if "%1"=="read" (
    python main.py read --config secrets\config.json --catalog catalog.json
) else (
    echo Unknown command: %1
    echo Use: check, discover, or read
)