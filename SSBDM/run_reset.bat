@echo off
echo Running database reset script...
powershell -ExecutionPolicy Bypass -File reset_db.ps1
pause 