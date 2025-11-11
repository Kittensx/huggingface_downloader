@echo off
setlocal enabledelayedexpansion

REM === Paths relative to this .bat ===
set "ROOT=%~dp0"
set "PS1=%ROOT%hf_download.ps1"
set "PY_SCRIPT=%ROOT%hf_grab.py"
set "VENV_ACT=%ROOT%venv\Scripts\activate.bat"
set "PY_EXE=%ROOT%venv\Scripts\python.exe"

REM === Check PS script exists ===
if not exist "%PS1%" (
  echo [ERROR] Cannot find hf_download.ps1 at "%PS1%"
  exit /b 2
)

REM === Activate venv if present ===
if exist "%VENV_ACT%" (
  call "%VENV_ACT%"
) else (
  echo [WARN] Virtual environment not found at "%VENV_ACT%". Using system Python.
)

REM === Unblock the PowerShell script silently (first-run on Windows) ===
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Unblock-File -LiteralPath '%PS1%' } catch {}" >nul 2>&1

REM === If venv python exists, pass it explicitly to PS script ===
set "PY_ARG="
if exist "%PY_EXE%" set "PY_ARG=-PythonExe ""%PY_EXE%"" "

REM === Always pass ScriptPath so PS doesn't have to guess ===
set "SCRIPT_ARG=-ScriptPath ""%PY_SCRIPT%"" "

REM === Help if no args ===
if "%~1"=="" (
  echo.
  echo Usage:
  echo   %~n0 "https://huggingface.co/owner/repo/tree/BRANCH[/sub/path]" "DEST_FOLDER" [additional hf_download.ps1 args]
  echo.
  echo Examples:
  echo   %~n0 "https://huggingface.co/acme/awesome-model/tree/main" ".\out"
  echo   %~n0 "https://huggingface.co/acme/awesome-model/tree/main/models/onnx" ".\onnx_only" -ForceTokenPrompt
  echo   %~n0 "https://huggingface.co/acme/private-model/tree/main" ".\out" -Token "hf_xxx"
  echo.
  echo Notes:
  echo   - All extra arguments are forwarded to hf_download.ps1.
  echo   - If VENV is present, it will be activated and its Python used.
  echo.
)

REM === Run the PowerShell wrapper, forwarding all user args ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %PY_ARG% %SCRIPT_ARG% %*

set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [ERROR] hf_download.ps1 exited with code %RC%
  exit /b %RC%
)

echo [OK] Done.
exit /b 0
