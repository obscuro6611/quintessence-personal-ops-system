@echo off
taskkill /FI "WINDOWTITLE eq Quintessence Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Quintessence Frontend*" /T /F >nul 2>&1
echo Quintessence windows stopped. If a window remains, close it manually.
pause
