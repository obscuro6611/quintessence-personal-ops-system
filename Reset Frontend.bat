@echo off
setlocal
cd /d "%~dp0frontend"
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
npm install
pause
endlocal
