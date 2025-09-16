@echo off
echo ========================================
echo    RoboRun GitHub Deployment Helper
echo ========================================
echo.

echo Step 1: Initializing Git repository...
git init

echo.
echo Step 2: Adding all files...
git add .

echo.
echo Step 3: Committing files...
git commit -m "Deploy RoboRun game to GitHub Pages"

echo.
echo Step 4: Please enter your GitHub username:
set /p GITHUB_USERNAME=

echo.
echo Step 5: Connecting to GitHub repository...
git remote add origin https://github.com/%GITHUB_USERNAME%/roborun.git

echo.
echo Step 6: Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo    Deployment Complete!
echo ========================================
echo.
echo Your game will be available at:
echo https://%GITHUB_USERNAME%.github.io/roborun/
echo.
echo Please wait 2-5 minutes for GitHub Pages to build.
echo.
pause
