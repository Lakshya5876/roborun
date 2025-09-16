# RoboRun - Web Edition

A fast-paced endless runner game built with Pygame, optimized for web deployment.

## 🎮 Game Features

- **Dynamic Scaling**: Automatically adapts to any screen size
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dual Controls**: Arrow keys or WASD for movement
- **Power-ups**: Invincibility, magnet, and bullet power-ups
- **Smooth Animations**: Pixel-perfect scaling with smooth animations
- **Start Screen**: Professional start screen with controls and instructions

## 🕹️ Controls

- **Movement**: Arrow Keys or WASD
- **Shoot**: Space (when powerup is active)
- **Pause**: Escape
- **Start/Restart**: R
- **Quit**: Q

## 🚀 Web Deployment

This game is designed to run in web browsers using Pygbag. The game automatically scales to fit any browser window size while maintaining aspect ratio.

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the game locally:
   ```bash
   python main.py
   ```

3. Build for web:
   ```bash
   python build_web.py
   ```

### GitHub Pages Deployment

The game is automatically deployed to GitHub Pages when pushed to the main branch. The web version will be available at:
`https://[your-username].github.io/roborun/`

## 🎯 Gameplay

- Control your robot character to avoid obstacles
- Collect coins to increase your score
- Use power-ups strategically:
  - **Invincibility**: Makes you invulnerable and increases speed
  - **Magnet**: Attracts nearby coins
  - **Bullet**: Shoot obstacles to clear your path
- Survive as long as possible to achieve a high score!

## 🛠️ Technical Details

- **Engine**: Pygame 2.5.2
- **Web Deployment**: Pygbag
- **Resolution**: 1024x768 base resolution with responsive scaling
- **Framerate**: 60 FPS
- **Browser Support**: Modern browsers with WebAssembly support

## 📁 Project Structure

```
roborun/
├── main.py              # Main game file
├── web_main.py          # Web-optimized version
├── build_web.py         # Web build script
├── requirements.txt     # Python dependencies
├── .github/workflows/   # GitHub Actions for deployment
├── robo.gif            # Player character sprite
├── enemy.gif           # Enemy sprite
└── README.md           # This file
```

## 🎨 Visual Design

The game features a clean, pixel-art style with:
- Smooth scaling that preserves pixel-perfect graphics
- Responsive design that works on all screen sizes
- Professional UI with clear instructions
- Consistent visual scaling across devices

## 🚀 Quick Start

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python main.py`
4. Press R to start playing!

## 🌐 Web Version

The web version automatically:
- Detects browser window size
- Scales the game to fit perfectly
- Maintains aspect ratio
- Works on desktop and mobile devices

Enjoy playing RoboRun! 🎮
