# RoboRun

Desktop (pygame) and Browser (HTML5 Canvas) builds.

## Desktop (keep main.py unchanged)

- Requires Python 3.10+
- Install deps:
  ```bash
  pip install -r requirements.txt
  ```
- Run:
  ```bash
  python main.py
  ```

## Browser (no build tools required)

- Files: `index.html`, `style.css`, `game.js`.
- Controls:
  - Arrow Keys or WASD — Move
  - SPACE — Shoot (when powerup active)
  - ESC — Pause
  - Q — Quit to Start (from Pause)
  - R — Start from Start screen, or Restart from Game Over
  - F — Toggle Fullscreen (Browser Only)
- Start screen shows “RoboRun”, controls, and “Press R to Play”.
- Game Over: Press R to restart directly (skips start screen).
- Pause: shows “Press Q to Quit” and a Quit button.
- Rendering: virtual resolution 960×720 with aspect-preserving scaling, centered.

### Local test

Open a local static server from this folder and visit `http://localhost:8000/`:
```bash
python -m http.server 8000
```

### Deploy to GitHub Pages

1. Create a new GitHub repo and push this folder (root contains `index.html`).
2. Enable Pages: Settings → Pages → Deploy from branch → `main` branch, `/ (root)`.
3. Wait for the Pages URL to become active; open it to play.

## Notes
- The web build mirrors the desktop gameplay and feel, including player/enemy, lasers, coins, powerups (invincibility/magnet/bullet), scoring, distance, speed scaling.
- The desktop build remains unchanged in `main.py`.
