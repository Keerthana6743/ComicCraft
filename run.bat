@echo off
title ComicCraft - AI Comic Story Creator

cd /d "%~dp0"

echo.
echo ==========================================
echo       ComicCraft - AI Comic Creator
echo ==========================================
echo.

if not exist "comiccraft-env\Scripts\python.exe" (
    echo [ERROR] ComicCraft virtual environment not found.
    echo.
    echo Please make sure the folder "comiccraft-env" exists.
    echo.
    pause
    exit /b 1
)

echo Starting ComicCraft...
echo.

start "ComicCraft Server" cmd /k ""%~dp0comiccraft-env\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

timeout /t 4 /nobreak >nul

start "" "http://127.0.0.1:8000"

echo.
echo ComicCraft is starting...
echo Browser will open automatically.
echo.