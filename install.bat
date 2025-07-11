@echo off
REM Claude MultiAgent Framework Installer for Windows
REM One-command installation script

echo 🧠 Claude MultiAgent Framework Installer
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed. Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create temporary directory
set TEMP_DIR=%TEMP%\claude-framework-install
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
cd /d "%TEMP_DIR%"

echo 📦 Downloading Claude MultiAgent Framework...

REM Download the latest release
curl -L -o framework.zip "https://github.com/4pach/Claude-MultiAgent-Framework/archive/refs/heads/main.zip"
tar -xf framework.zip
cd Claude-MultiAgent-Framework-main

echo 🔧 Installing dependencies...

REM Install framework
pip install -e .

echo 🎯 Testing installation...

REM Test if CLI works
claude-framework --help >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installation completed but CLI may need PATH update
    echo Try restarting your command prompt
) else (
    echo ✅ CLI command 'claude-framework' is ready!
)

REM Cleanup
cd ..
rmdir /s /q "%TEMP_DIR%"

echo.
echo 🎉 Installation complete!
echo.
echo Quick start:
echo   claude-framework create --name MyProject --type telegram_bot
echo.
echo Documentation: https://github.com/4pach/Claude-MultiAgent-Framework
echo Support: https://boosty.to/4pach
echo.
pause
