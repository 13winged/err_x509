@echo off
chcp 65001 >nul
echo Quick Test Script for err_x509
echo ================================
echo.

if not exist err_x509.exe (
    echo ❌ ERROR: err_x509.exe not found!
    echo Run build.bat first to compile the program.
    pause
    exit /b 1
)

echo Creating test configuration...
(
echo port: 7890
echo proxies:
echo   - { name: Test-Server-1, type: trojan, server: test1.example.com, port: 443, password: test-pass-123 }
echo   - { name: Test-Server-2, type: vmess, server: test2.example.com, port: 443, uuid: 12345678-1234-1234-1234-123456789012 }
) > x509_no_fix.yaml

echo.
echo Running err_x509.exe...
echo ========================
err_x509.exe

echo.
if exist x509_fixed.yaml (
    echo ✅ SUCCESS: x509_fixed.yaml created!
    echo.
    echo Contents of x509_fixed.yaml:
    echo ------------------------------
    type x509_fixed.yaml
    echo ------------------------------
    
    echo.
    echo Verification:
    findstr /c:"skip-cert-verify" x509_fixed.yaml
    if %ERRORLEVEL% EQU 0 (
        echo ✅ skip-cert-verify was added successfully!
    ) else (
        echo ❌ ERROR: skip-cert-verify was NOT added!
    )
) else (
    echo ❌ ERROR: x509_fixed.yaml was not created!
)

echo.
echo Cleaning up test files...
if exist x509_no_fix.yaml del x509_no_fix.yaml
if exist x509_fixed.yaml del x509_fixed.yaml

echo.
echo Test complete.
pause