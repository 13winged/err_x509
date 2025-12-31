@echo off
chcp 65001 >nul

echo.
echo ╔═══════════════════════════════════════════════╗
echo ║            err_x509 - x509 SSL Fixer          ║
echo ║          Fix Clash SSL certificate errors     ║
echo ╚═══════════════════════════════════════════════╝
echo.

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    where python3 >nul 2>nul
    if %errorlevel% neq 0 (
        echo ❌ Python not found!
        echo Please install Python 3 from python.org
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

REM Run err_x509
%PYTHON% -m err_x509 %*

if %errorlevel% equ 0 (
    echo.
    echo ✅ Operation completed successfully!
) else (
    echo.
    echo ❌ Operation failed!
)

if "%1"=="" pause