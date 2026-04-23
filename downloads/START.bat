@echo off
:: Sarva Node — One-Click Installer for Windows
:: Just double-click this file. No install needed.
title Sarva Node
color 0A
echo.
echo  ██████╗  ██████╗ ██████╗ 
echo  ██╔══██╗██╔═══██╗██╔══██╗
echo  ██████╔╝██║   ██║██████╔╝
echo  ██╔═══╝ ██║   ██║██╔══██╗
echo  ██║     ╚██████╔╝██║  ██║
echo  ╚═╝      ╚═════╝ ╚═╝  ╚═╝
echo.
echo  Decentralized Compute Node
echo  =============================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found. Installing...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe -OutFile python-installer.exe"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo [+] Python installed!
)

:: Set environment (hardcoded API)
set SARVA_API=https://e65440d9-cfb0-47fa-b11a-d2070bf13013.up.railway.app
set SARVA_NODE_NAME=%COMPUTERNAME%-windows
set SARVA_GPU_TIER=cpu
set SARVA_OWNER_ID=anonymous
set SARVA_REGION=in

echo [i] API: %SARVA_API%
echo [i] Node Name: %SARVA_NODE_NAME%
echo.
echo Starting Sarva Node...
echo If this is your first time, enter your User ID when prompted.
echo Press Ctrl+C to stop.
echo.
python "%~dp0agent.py"
pause