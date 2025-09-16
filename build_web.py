#!/usr/bin/env python3
"""
Build script for creating web deployment of RoboRun using Pygbag.
"""

import subprocess
import sys
import os

def build_web():
    """Build the game for web deployment using Pygbag"""
    try:
        # Install pygbag if not already installed
        print("Installing Pygbag...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pygbag"], check=True)
        
        # Build the web version
        print("Building web version...")
        cmd = [
            sys.executable, "-m", "pygbag",
            "--title", "RoboRun",
            "--icon", "robo.gif",
            "--template", "default",
            "--cdn", "https://pygame-web.github.io/archives/",
            "main.py"
        ]
        
        subprocess.run(cmd, check=True)
        print("Web build completed successfully!")
        print("The game is now ready for deployment in the build/web/ directory")
        
    except subprocess.CalledProcessError as e:
        print(f"Error building web version: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_web()
