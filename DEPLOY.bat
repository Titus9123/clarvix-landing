@echo off
title Clarvix Deploy to GitHub Pages
echo.
echo ==========================================
echo   CLARVIX - Deploy to GitHub Pages
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking git status...
git status
echo.

echo [2/3] Adding all changes...
git add -A
echo.

set /p msg="Enter commit message (or press Enter for default): "
if "%msg%"=="" set msg=Update landing page

echo [3/3] Committing and pushing...
git commit -m "%msg%"
git push origin main
echo.

echo ==========================================
echo   DONE! Site updating at clarvix.net
echo   (wait ~30-60 seconds for GitHub)
echo ==========================================
pause
