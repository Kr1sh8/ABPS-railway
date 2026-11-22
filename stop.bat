@echo off
echo Stopping ABPS servers...
taskkill /F /FI "WINDOWTITLE eq ABPS Backend*" 2>nul
taskkill /F /FI "WINDOWTITLE eq ABPS Dashboard*" 2>nul
taskkill /F /IM "uvicorn.exe" 2>nul
echo Done.
pause
