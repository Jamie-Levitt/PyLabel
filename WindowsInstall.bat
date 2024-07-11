@echo off
setlocal enabledelayedexpansion

REM Check if the script is run as an administrator
net session >nul 2>&1
if not %errorlevel%==0 (
    echo Requesting administrative privileges...
    powershell -command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

REM Set the installation directory to User's Program Files
set "PROGRAM_FILES=%ProgramFiles%\PyLabel"

REM Create the directory if it doesn't exist
if not exist "%PROGRAM_FILES%" (
    mkdir "%PROGRAM_FILES%"
)

REM Assign administrative permissions to the directory
echo Granting administrative permissions to %PROGRAM_FILES%...
icacls "%PROGRAM_FILES%" /grant:r "%USERNAME%:(OI)(CI)F" /inheritance:e /T

REM Flag to indicate if Python version is found
set found_python=false

REM Set the directory path where your scripts are installed
set "SCRIPT_DIR=%~dp0\PyLabelProgramFiles"

echo Installing files from %SCRIPT_DIR% to %PROGRAM_FILES%\PyLabel...
xcopy "%SCRIPT_DIR%" "%PROGRAM_FILES%\" /s /y /exclude:%~dp0exclude.txt

cd %PROGRAM_FILES%
icacls "Roboto-Regular.ttf" /grant Users:F

REM Grant administrative permissions to all .py files
echo Granting administrative permissions to all Python files...
for /r "%PROGRAM_FILES%" %%f in (*.py) do (
    icacls "%%f" /grant:r "%USERNAME%:(OI)(CI)F" /inheritance:e /T
)

REM Check for Python 3.11.9
for /f "tokens=*" %%i in ('where python') do (
    call :check_version "%%i"
)
goto :end

:check_version
for /f "tokens=*" %%v in ('%~1 --version 2^>^&1') do (
    for /f "tokens=2 delims= " %%v in ("%%v") do (
        echo Detected Python version %%v from %~1
        set version=%%v
        set py_path=%~1
        goto :parse_version
    )
)

:parse_version
REM Extract the major, minor, and patch versions
for /f "tokens=1-3 delims=." %%a in ("%version%") do (
    set major=%%a
    set minor=%%b
    set patch=%%c
)

if "%major%.%minor%.%patch%" == "3.11.9" (
    echo Correct Python version found at %py_path%
    set found_python=true
    goto :install_dependencies
)

goto :EOF

:install_dependencies
cd %PROGRAM_FILES%
echo Installing dependencies...

REM Verify the existence of requirements.txt
if not exist requirements.txt (
    echo requirements.txt not found!
    pause
    goto :end
)

REM Install dependencies
"%py_path%" -m ensurepip
"%py_path%" -m pip install --upgrade pip
"%py_path%" -m pip install -r requirements.txt

REM Set up PyLabel command
echo @echo off > %SystemRoot%\System32\PyLabel.bat
echo %py_path% "%PROGRAM_FILES%\PyLabel.py" %%* >> %SystemRoot%\System32\PyLabel.bat

REM Append %PROGRAM_FILES% to PATH if not already present
echo Checking PATH for %PROGRAM_FILES%...
echo %PATH% | findstr /I /C:"%PROGRAM_FILES%" >nul
if %errorlevel% neq 0 (
    echo Adding %PROGRAM_FILES% to PATH
    setx PATH "%PROGRAM_FILES%"
) else (
    echo %PROGRAM_FILES% is already in PATH
)

echo Installation complete.
echo You can now use the command 'PyLabel' from any directory

pause
goto :end

:end
if not "%found_python%"=="true" (
    echo Python 3.11.9 is not installed.
    start "%PROGRAM_FILES%\PyLabel\PyInstructions.pdf"
    pause
)
endlocal
goto :EOF
