# 🚀 RoboRun GitHub Pages Deployment Guide

This guide will help you deploy your RoboRun game to GitHub Pages so everyone can play it by clicking a URL.

## 📋 Prerequisites

- GitHub account (free)
- Git installed on your computer
- Python 3.9+ installed

## 🎯 Step-by-Step Deployment

### **Step 1: Create GitHub Repository**

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon → **"New repository"**
3. Repository name: `roborun` (or your preferred name)
4. Description: `"RoboRun - A fast-paced endless runner game"`
5. Make it **Public** (required for free GitHub Pages)
6. **Don't** check "Add a README file"
7. Click **"Create repository"**

### **Step 2: Upload Your Game Files**

Open Command Prompt or PowerShell in your project folder and run:

```bash
# Initialize Git repository
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit: RoboRun game with web deployment"

# Connect to GitHub (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/roborun.git

# Push to GitHub
git push -u origin main
```

### **Step 3: Enable GitHub Pages**

1. Go to your repository on GitHub
2. Click **"Settings"** tab
3. Scroll down to **"Pages"** in the left sidebar
4. Under **"Source"**, select **"GitHub Actions"**
5. The deployment will start automatically

### **Step 4: Wait for Deployment**

1. Go to **"Actions"** tab in your repository
2. You'll see a workflow called "Deploy RoboRun to GitHub Pages"
3. Wait for it to complete (usually 2-5 minutes)
4. Once complete, you'll see a green checkmark

### **Step 5: Access Your Game**

Your game will be available at:
```
https://YOUR_USERNAME.github.io/roborun/
```

## 🔧 Troubleshooting

### **If deployment fails:**
1. Check the **"Actions"** tab for error messages
2. Make sure all files are uploaded correctly
3. Ensure the repository is public

### **If game doesn't load:**
1. Check browser console for errors (F12)
2. Make sure all asset files are present
3. Try refreshing the page

### **If you need to update the game:**
```bash
# Make your changes to the code
git add .
git commit -m "Update game features"
git push origin main
```

## 📱 Features of Your Deployed Game

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Professional UI**: Clean start screen and controls
- **Smooth Scaling**: Adapts to any screen size
- **Dual Controls**: Arrow keys and WASD
- **Web Optimized**: Fast loading and smooth gameplay

## 🌐 Sharing Your Game

Once deployed, you can share your game with anyone using the URL:
```
https://YOUR_USERNAME.github.io/roborun/
```

## 🎮 Game Controls

- **Movement**: Arrow Keys or WASD
- **Shoot**: Space (when powerup active)
- **Start/Restart**: R
- **Pause**: ESC
- **Quit**: Q (when paused)

## 📊 Repository Structure

Your repository should contain:
```
roborun/
├── main.py              # Main game file
├── build_github.py      # Build script
├── index.html           # Web interface
├── requirements.txt     # Dependencies
├── .github/workflows/   # Deployment automation
├── robo.gif            # Player sprite
├── enemy.gif           # Enemy sprite
└── README.md           # Documentation
```

## 🎯 Success!

Once deployed, your RoboRun game will be:
- ✅ Playable by anyone with the URL
- ✅ Responsive on all devices
- ✅ Professionally presented
- ✅ Easy to share and embed

Enjoy your deployed game! 🎮
