@echo off
if "%~1"=="-Z1" (
  tar.exe -tf "%~2"
  exit /b %ERRORLEVEL%
)
if "%~1"=="-p" (
  tar.exe -xOf "%~2" "%~3"
  exit /b %ERRORLEVEL%
)
tar.exe %*
exit /b %ERRORLEVEL%
