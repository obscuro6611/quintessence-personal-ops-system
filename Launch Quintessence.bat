@echo off
setlocal
set "ROOT=%~dp0"
cd /d "%ROOT%"
echo ============================================
echo   Quintessence Local Launcher
echo ============================================
if not exist "backend" (echo ERROR: backend folder not found.& pause& exit /b 1)
if not exist "frontend" (echo ERROR: frontend folder not found.& pause& exit /b 1)
cd /d "%ROOT%backend"
if not exist ".venv\Scripts\activate.bat" py -3.12 -m venv .venv
call .venv\Scripts\activate.bat
if not exist ".env" copy ".env.example" ".env" >nul
python -m pip install -r requirements.txt
start "Quintessence Backend" cmd /k "cd /d ""%ROOT%backend"" && call .venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
cd /d "%ROOT%frontend"
if not exist ".env" copy ".env.example" ".env" >nul
if not exist "node_modules" npm install
start "Quintessence Frontend" cmd /k "cd /d ""%ROOT%frontend"" && npm run dev"
timeout /t 6 /nobreak >nul
start http://localhost:5173
endlocal
