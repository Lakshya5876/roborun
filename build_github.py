#!/usr/bin/env python3
"""
Build script for GitHub Pages deployment of RoboRun.
"""

import subprocess
import sys
import os

def build_for_github():
    """Build the game for GitHub Pages deployment"""
    try:
        print("Building RoboRun for GitHub Pages...")
        
        # Install pygbag
        print("Installing Pygbag...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pygbag"], check=True)
        
        # Build the web version
        print("Building web version...")
        cmd = [
            sys.executable, "-m", "pygbag",
            "--title", "RoboRun",
            "--icon", "robo.gif",
            "--template", "default",
            "--cdn", "https://pygame-web.github.io/archives/0.9/",
            "--build",
            "main.py"
        ]
        
        subprocess.run(cmd, check=True)
        print("Web build completed successfully!")
        print("Files are ready in the build/web/ directory")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error building web version: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    build_for_github()
