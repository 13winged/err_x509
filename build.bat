@echo off
chcp 65001 >nul
echo ========================================================
echo            err_x509 - Build Script
echo ========================================================
echo.
echo This script will compile err_x509.exe from source code.
echo Make sure you have Go installed: https://golang.org/dl/
echo.

REM Check if Go is installed
where go >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Go is not installed or not in PATH!
    echo.
    echo Please install Go from: https://golang.org/dl/
    echo After installation, restart your computer or command prompt.
    echo.
    pause
    exit /b 1
)

REM Check Go version
echo Checking Go version...
for /f "tokens=3" %%i in ('go version') do set "GOVERSION=%%i"
echo ✅ Go version: %GOVERSION%
echo.

REM Clean previous builds
if exist err_x509.exe (
    echo Removing previous err_x509.exe...
    del err_x509.exe
)

if exist err_x509 (
    echo Removing previous err_x509 (Linux/Mac)...
    del err_x509
)

echo.
echo ========================================================
echo 1. Building for Windows (err_x509.exe)...
echo ========================================================
go build -ldflags "-s -w" -o err_x509.exe main.go

if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Failed to build for Windows!
    pause
    exit /b 1
)

if exist err_x509.exe (
    echo ✅ Successfully built: err_x509.exe
    echo    Size: %~z0 bytes
) else (
    echo ❌ ERROR: err_x509.exe was not created!
    pause
    exit /b 1
)

echo.
echo ========================================================
echo 2. Building for Linux/Mac (optional)...
echo ========================================================
set /p buildOther=Do you want to build for Linux/Mac too? (y/N): 
if /i "%buildOther%"=="y" (
    echo.
    echo Building for Linux...
    set GOOS=linux
    set GOARCH=amd64
    go build -ldflags "-s -w" -o err_x509_linux main.go
    
    echo Building for Mac...
    set GOOS=darwin
    set GOARCH=amd64
    go build -ldflags "-s -w" -o err_x509_mac main.go
    
    if exist err_x509_linux (
        echo ✅ Successfully built: err_x509_linux
    )
    if exist err_x509_mac (
        echo ✅ Successfully built: err_x509_mac
    )
)

echo.
echo ========================================================
echo 3. Creating example files...
echo ========================================================
if not exist example_x509_no_fix.yaml (
    echo Creating example_x509_no_fix.yaml...
    (
echo port: 7890
echo socks-port: 7891
echo redir-port: 7892
echo allow-lan: false
echo mode: global
echo log-level: info
echo external-controller: '127.0.0.1:9090'
echo.
echo proxies:
echo   - { name: Moldova, type: trojan, server: morse-stank-most.data-hub.online, port: 443, password: 1597b90e-c9b2-4407-bd53-60807bf74070 }
echo   - { name: Netherlands, type: trojan, server: acre-cable-skip.data-hub.online, port: 443, password: 1597b90e-c9b2-4407-bd53-60807bf74070 }
echo   - { name: Portugal, type: trojan, server: eats-rigor-judge.data-hub.online, port: 443, password: 1597b90e-c9b2-4407-bd53-60807bf74070 }
    ) > example_x509_no_fix.yaml
    echo ✅ Created: example_x509_no_fix.yaml
) else (
    echo ℹ️  example_x509_no_fix.yaml already exists
)

echo.
echo ========================================================
echo 4. Running tests...
echo ========================================================
set /p runTest=Do you want to run a test? (y/N): 
if /i "%runTest%"=="y" (
    echo.
    echo Copying example to test...
    copy example_x509_no_fix.yaml x509_no_fix.yaml >nul
    
    echo Running err_x509.exe...
    echo ========================= OUTPUT =========================
    err_x509.exe
    echo ==========================================================
    
    if exist x509_fixed.yaml (
        echo.
        echo ✅ Test successful! Check x509_fixed.yaml
        echo.
        echo Showing first few lines of output:
        echo ----------------------------------------------------------
        type x509_fixed.yaml | findstr /n /c:"proxies:" /c:"skip-cert-verify"
        echo ----------------------------------------------------------
    ) else (
        echo ❌ ERROR: x509_fixed.yaml was not created!
    )
    
    REM Clean up test files
    if exist x509_no_fix.yaml del x509_no_fix.yaml
)

echo.
echo ========================================================
echo 🎉 BUILD COMPLETED SUCCESSFULLY!
echo ========================================================
echo.
echo Files created in this folder:
if exist err_x509.exe echo   📄 err_x509.exe      - Windows executable
if exist err_x509_linux echo   🐧 err_x509_linux    - Linux executable
if exist err_x509_mac echo   🍎 err_x509_mac      - macOS executable
echo   📋 example_x509_no_fix.yaml - Example configuration file
echo.
echo Next steps:
echo 1. Copy err_x509.exe to your desired folder
echo 2. Create x509_no_fix.yaml with your configuration
echo 3. Run err_x509.exe
echo 4. Use the generated x509_fixed.yaml
echo.
echo Press any key to exit...
pause >nul