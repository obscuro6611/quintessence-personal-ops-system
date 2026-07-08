@echo off
setlocal
set "ROOT=%~dp0"
cd /d "%ROOT%"
if not exist backups mkdir backups
set STAMP=%DATE:~-4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set STAMP=%STAMP: =0%
powershell -NoProfile -Command "Compress-Archive -Path 'backend\data','backend\storage' -DestinationPath ('backups\quintessence_manual_backup_%STAMP%.zip') -Force"
echo Backup created in backups folder.
pause
endlocal
