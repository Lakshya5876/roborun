// RoboRun - Web Edition (vanilla JS + Canvas)
// Keeps main.py untouched; replicates gameplay feel and controls.

(() => {
  const BASE_WIDTH = 960;
  const BASE_HEIGHT = 720;
  const FPS = 60;

  const canvas = document.getElementById('game');
  const ctx = canvas.getContext('2d');
  ctx.imageSmoothingEnabled = true;

  // UI Elements
  const overlay = document.getElementById('overlay');
  const startPanel = document.getElementById('start');
  const pausePanel = document.getElementById('pause');
  const gameoverPanel = document.getElementById('gameover');
  const startBtn = document.getElementById('startBtn');
  const quitBtn = document.getElementById('quitBtn');
  const restartBtn = document.getElementById('restartBtn');
  const scoreLine = document.getElementById('scoreLine');
  const highScoreLine = document.getElementById('highScoreLine');

  // Scaling to fit viewport, preserving aspect ratio, centered, no black bars outside viewport
  let scale = 1;
  let letterboxX = 0;
  let letterboxY = 0;
  function layout() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const sx = vw / BASE_WIDTH;
    const sy = vh / BASE_HEIGHT;
    scale = Math.min(sx, sy);
    const ww = Math.floor(BASE_WIDTH * scale);
    const hh = Math.floor(BASE_HEIGHT * scale);
    letterboxX = Math.floor((vw - ww) / 2);
    letterboxY = Math.floor((vh - hh) / 2);
    canvas.style.width = `${ww}px`;
    canvas.style.height = `${hh}px`;
    canvas.style.transform = '';
    canvas.style.position = '';
    canvas.width = BASE_WIDTH;
    canvas.height = BASE_HEIGHT;
  }
  window.addEventListener('resize', layout);
  layout();

  // Fullscreen toggle (browser only)
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      canvas.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  }

  // Input handling
  const keys = new Set();
  window.addEventListener('keydown', (e) => {
    keys.add(e.key.toLowerCase());
    if (state === 'start' && e.key.toLowerCase() === 'r') startGame();
    if (state === 'gameover' && e.key.toLowerCase() === 'r') restartGame();
    if (e.key.toLowerCase() === 'f') toggleFullscreen();
    if (e.key === ' ') e.preventDefault();
  });
  window.addEventListener('keyup', (e) => keys.delete(e.key.toLowerCase()));

  startBtn.addEventListener('click', () => startGame());
  restartBtn.addEventListener('click', () => restartGame());
  quitBtn.addEventListener('click', () => quitToStart());

  // Assets (use existing gifs if present)
  const playerImg = new Image();
  playerImg.src = 'robo.gif';
  const enemyImg = new Image();
  enemyImg.src = 'enemy.gif';

  // Colors
  const WHITE = '#ffffff';
  const RED = '#ff0000';
  const YELLOW = '#ffff00';
  const GREEN = '#00ff00';
  const BLUE = '#00a2ff';
  const DARK_GREY = '#1e1e1e';
  const LIGHT_GREY = '#c8c8c8';

  // Game state
  let state = 'start'; // start | playing | paused | gameover
  let highScore = 0;

  class Player {
    constructor() {
      this.width = 120;
      this.height = 120;
      this.x = BASE_WIDTH / 2 - this.width / 2;
      this.y = BASE_HEIGHT - 100 - this.height / 2;
      this.baseSpeed = 5;
      this.speed = 5;
      this.invincible = false;
      this.magnet = false;
      this.canShoot = false;
      this.powerupStart = 0;
      this.coins = 0;
      this.distance = 0;
      this.hitTimer = 0;
      this.lastShotAt = 0;
      this.shootCooldownMs = 300;
    }
    rect() { return { x: this.x, y: this.y, w: this.width, h: this.height }; }
    hitbox() {
      const shrink = Math.floor(this.width / 5);
      return { x: this.x + shrink, y: this.y + shrink, w: this.width - 2*shrink, h: this.height - 2*shrink };
    }
    move() {
      const left = keys.has('arrowleft') || keys.has('a');
      const right = keys.has('arrowright') || keys.has('d');
      const up = keys.has('arrowup') || keys.has('w');
      const down = keys.has('arrowdown') || keys.has('s');
      if (left) this.x = Math.max(0, this.x - this.speed);
      if (right) this.x = Math.min(BASE_WIDTH - this.width, this.x + this.speed);
      if (up) this.y = Math.max(0, this.y - this.speed);
      if (down) this.y = Math.min(BASE_HEIGHT - this.height, this.y + this.speed);
    }
    updatePowerup(now) {
      if (this.invincible || this.magnet || this.canShoot) {
        if (now - this.powerupStart > 10000) {
          if (this.invincible) { this.invincible = false; return 'Invincibility Expired!'; }
          if (this.magnet) { this.magnet = false; return 'Magnet Power Expired!'; }
          if (this.canShoot) { this.canShoot = false; return 'Bullet Power Expired!'; }
        }
      }
      return null;
    }
    shoot(now) {
      if (this.canShoot && now - this.lastShotAt >= this.shootCooldownMs) {
        this.lastShotAt = now;
        return new Bullet(this.x + this.width/2, this.y);
      }
      return null;
    }
    draw() {
      if (this.hitTimer > 0 && Math.floor(this.hitTimer / 2) % 2 === 0) return;
      if (playerImg.complete && playerImg.naturalWidth > 0) {
        ctx.drawImage(playerImg, this.x, this.y, this.width, this.height);
      } else {
        ctx.fillStyle = this.invincible ? GREEN : BLUE;
        ctx.fillRect(this.x, this.y, this.width, this.height);
      }
    }
  }

  class Bullet {
    constructor(x, y) {
      this.x = x;
      this.y = y;
      this.speed = 10;
      this.radius = 5;
      this.trail = [];
      this.active = true;
    }
    update() {
      this.y -= this.speed;
      if (Math.random() < 0.3) this.trail.push({ x: this.x + (Math.random()*4-2), y: this.y + (Math.random()*4-2), life: 10 });
      this.trail.forEach(p => p.life--);
      this.trail = this.trail.filter(p => p.life > 0);
      if (this.y < -this.radius) this.active = false;
    }
    draw() {
      for (const p of this.trail) {
        const alpha = Math.floor(255 * (p.life / 10));
        ctx.fillStyle = `rgba(100,200,255,${alpha/255})`;
        ctx.beginPath(); ctx.arc(p.x, p.y, 2, 0, Math.PI*2); ctx.fill();
      }
      ctx.fillStyle = BLUE; ctx.beginPath(); ctx.arc(this.x, this.y, this.radius, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = WHITE; ctx.beginPath(); ctx.arc(this.x, this.y, this.radius-2, 0, Math.PI*2); ctx.fill();
    }
    rect() { return { x: this.x - this.radius, y: this.y - this.radius, w: this.radius*2, h: this.radius*2 }; }
  }

  class Obstacle {
    constructor(x, y) {
      this.type = 'drone';
      this.width = 144; this.height = 144;
      this.x = x; this.y = y;
    }
    get hitbox() { return { x: this.x + this.width/4, y: this.y + this.height/4, w: this.width/2, h: this.height/2 }; }
    update(speed) { this.y += speed; }
    draw() {
      if (enemyImg.complete && enemyImg.naturalWidth > 0) {
        ctx.drawImage(enemyImg, this.x, this.y, this.width, this.height);
      } else {
        ctx.fillStyle = '#ff00ff';
        ctx.fillRect(this.x, this.y, this.width, this.height);
      }
    }
  }

  class Laser {
    constructor(x1, y1, x2, y2) {
      const maxLen = BASE_WIDTH * 0.7;
      const dx = x2 - x1, dy = y2 - y1;
      const len = Math.hypot(dx, dy) || 1;
      if (len > maxLen) { const s = maxLen / len; x2 = x1 + dx * s; y2 = y1 + dy * s; }
      this.x1 = x1; this.y1 = y1; this.x2 = x2; this.y2 = y2;
      this.box1 = { x: x1 - 10, y: y1 - 10, w: 20, h: 20 };
      this.box2 = { x: x2 - 10, y: y2 - 10, w: 20, h: 20 };
      this.pulse = 0;
      this.pulseSpeed = 0.2;
    }
    update(speed) {
      this.y1 += speed; this.y2 += speed; this.box1.y += speed; this.box2.y += speed; this.pulse += this.pulseSpeed;
    }
    draw() {
      const pulse = Math.abs(Math.sin(this.pulse)) * 0.3 + 0.7;
      const boxes = [this.box1, this.box2];
      for (const b of boxes) {
        const glowAlpha = Math.floor(100 * pulse);
        ctx.fillStyle = `rgba(255,0,0,${glowAlpha/255})`;
        ctx.fillRect(b.x - 10, b.y - 10, b.w + 20, b.h + 20);
        ctx.fillStyle = RED; ctx.fillRect(b.x, b.y, b.w, b.h);
      }
      for (let w = 8; w > 3; w--) {
        const alpha = Math.floor(100 * pulse * (w / 8));
        ctx.strokeStyle = `rgba(255,0,0,${alpha/255})`;
        ctx.lineWidth = w;
        ctx.beginPath(); ctx.moveTo(this.x1, this.y1); ctx.lineTo(this.x2, this.y2); ctx.stroke();
      }
      ctx.strokeStyle = RED; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(this.x1, this.y1); ctx.lineTo(this.x2, this.y2); ctx.stroke();
    }
    collides(rect) {
      const lineRect = { x: Math.min(this.x1, this.x2) - 5, y: Math.min(this.y1, this.y2) - 5, w: Math.abs(this.x2 - this.x1) + 10, h: Math.abs(this.y2 - this.y1) + 10 };
      if (!rectsOverlap(lineRect, rect)) return false;
      const points = [
        {x: rect.x, y: rect.y}, {x: rect.x + rect.w, y: rect.y},
        {x: rect.x, y: rect.y + rect.h}, {x: rect.x + rect.w, y: rect.y + rect.h},
        {x: rect.x + rect.w/2, y: rect.y + rect.h/2},
      ];
      const dx = this.x2 - this.x1, dy = this.y2 - this.y1; const denom = dx*dx + dy*dy || 1;
      for (const p of points) {
        const t = Math.max(0, Math.min(1, ((p.x - this.x1)*dx + (p.y - this.y1)*dy) / denom));
        const cx = this.x1 + t * dx, cy = this.y1 + t * dy;
        const dist = Math.hypot(p.x - cx, p.y - cy);
        if (dist < 6) return true;
      }
      return false;
    }
  }

  class Coin {
    constructor(x, y) {
      this.x = x; this.y = y; this.collected = false; this.radius = 10;
    }
    update(speed) { this.y += speed; }
    draw() {
      if (this.collected) return;
      ctx.fillStyle = YELLOW; ctx.beginPath(); ctx.arc(this.x, this.y, this.radius, 0, Math.PI*2); ctx.fill();
    }
    rect() { return { x: this.x - this.radius, y: this.y - this.radius, w: this.radius*2, h: this.radius*2 }; }
  }

  class PowerUp {
    constructor(x, y, type) {
      this.x = x; this.y = y; this.w = 45; this.h = 45; this.type = type; this.pulse = 0; this.rot = 0;
    }
    update(speed) { this.y += speed; this.pulse += 0.1; this.rot = (this.rot + 2) % 360; }
    draw() {
      const pulse = Math.abs(Math.sin(this.pulse)) * 0.3 + 0.7;
      const glow = Math.floor(100 * pulse);
      const color = this.type === 'invincibility' ? '#00ff00' : (this.type === 'magnet' ? '#ffa500' : '#00a2ff');
      ctx.fillStyle = `rgba(${hexToRgb(color)},${glow/255})`;
      ctx.fillRect(this.x - 15, this.y - 15, this.w + 30, this.h + 30);
      ctx.fillStyle = color; ctx.fillRect(this.x, this.y, this.w, this.h);
      ctx.strokeStyle = WHITE; ctx.lineWidth = 3;
      if (this.type === 'invincibility') {
        const cx = this.x + this.w/2, cy = this.y + this.h/2;
        ctx.beginPath();
        ctx.moveTo(cx, this.y + 8);
        ctx.lineTo(this.x + this.w - 8, cy);
        ctx.lineTo(cx, this.y + this.h - 8);
        ctx.lineTo(this.x + 8, cy);
        ctx.closePath();
        ctx.stroke();
      } else if (this.type === 'magnet') {
        ctx.strokeRect(this.x + this.w/2 - 6, this.y + this.h/2 - 9, 12, 18);
        for (let i=0;i<3;i++) { const yy = this.y + this.h/2 + 9 + i*6; ctx.beginPath(); ctx.moveTo(this.x + this.w/2 - 12, yy); ctx.lineTo(this.x + this.w/2 + 12, yy); ctx.stroke(); }
      } else if (this.type === 'bullet') {
        ctx.fillStyle = WHITE; ctx.fillRect(this.x + this.w/2 - 4, this.y + this.h/2 - 10, 8, 20);
        ctx.beginPath(); ctx.arc(this.x + this.w/2, this.y + this.h/2 - 10, 4, 0, Math.PI*2); ctx.fill();
      }
    }
    rect() { return { x: this.x, y: this.y, w: this.w, h: this.h }; }
  }

  function rectsOverlap(a, b) { return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y; }

  function findSafePos(w, h, objects, tries=10) {
    for (let i=0;i<tries;i++) {
      const x = Math.floor(Math.random() * (BASE_WIDTH - w));
      const y = -h;
      const r = { x, y, w, h };
      if (!objects.some(o => {
        const ro = o.rect ? o.rect() : (o.hitbox ? o.hitbox : (o.box1 ? {x:o.box1.x,y:o.box1.y,w:o.box1.w,h:o.box1.h} : null));
        if (!ro) return false;
        const exp = { x: ro.x - 30, y: ro.y - 30, w: ro.w + 60, h: ro.h + 60 };
        return rectsOverlap(exp, r);
      })) return {x,y};
    }
    return null;
  }

  function ensureSafePath(objects) {
    const laneWidth = Math.floor(BASE_WIDTH / 3);
    for (let lane = 0; lane < 3; lane++) {
      const laneRect = { x: lane*laneWidth, y: 0, w: laneWidth, h: BASE_HEIGHT };
      const blocked = objects.some(o => rectsOverlap(laneRect, o.hitbox ? o.hitbox : (o.rect ? o.rect() : {x:o.x,y:o.y,w:o.w||0,h:o.h||0})));
      if (!blocked) return true;
    }
    return false;
  }

  function spawnCoinLine(baseX, objects, coins) {
    const spacing = 40; const len = 5;
    for (let i=0;i<len;i++) {
      const cx = baseX + Math.floor(Math.random()*21 - 10);
      const cy = -i * spacing;
      const coin = new Coin(cx, cy);
      const r = coin.rect();
      const blocked = objects.some(o => {
        const ro = o.hitbox ? o.hitbox : (o.rect ? o.rect() : null);
        if (!ro) return false;
        const exp = { x: ro.x - 30, y: ro.y - 30, w: ro.w + 60, h: ro.h + 60 };
        return rectsOverlap(exp, r);
      });
      if (!blocked) coins.push(coin);
    }
  }

  // Game variables
  let player, obstacles, lasers, coins, powerups, bullets, explosions;
  let baseSpeed, scrollSpeed, spawnTimer, laserTimer, coinTimer, running, paused, lastCheckpoint, difficulty, screenShake, powerupText, powerupTimer, gameStartAt, speedMultiplier, score;

  function resetRound() {
    player = new Player();
    obstacles = []; lasers = []; coins = []; powerups = []; bullets = []; explosions = [];
    baseSpeed = 5; scrollSpeed = baseSpeed; spawnTimer = 0; laserTimer = 0; coinTimer = 0;
    running = true; paused = false; lastCheckpoint = 0; difficulty = 1; screenShake = 0;
    powerupText = null; powerupTimer = 0; gameStartAt = performance.now(); speedMultiplier = 1.0; score = 0;
  }

  function startGame() { state = 'playing'; hideAllPanels(); resetRound(); }
  function restartGame() { state = 'playing'; hideAllPanels(); resetRound(); }
  function quitToStart() { state = 'start'; showStart(); }

  function hideAllPanels() {
    overlay.classList.add('hidden');
    startPanel.classList.add('hidden');
    pausePanel.classList.add('hidden');
    gameoverPanel.classList.add('hidden');
  }
  function showStart() {
    overlay.classList.remove('hidden');
    startPanel.classList.remove('hidden');
    pausePanel.classList.add('hidden');
    gameoverPanel.classList.add('hidden');
  }
  function showPause() {
    overlay.classList.remove('hidden');
    pausePanel.classList.remove('hidden');
  }
  function showGameover() {
    overlay.classList.remove('hidden');
    gameoverPanel.classList.remove('hidden');
  }

  // Text
  function drawText(text, x, y, size = 24, color = WHITE) {
    ctx.fillStyle = color;
    ctx.font = `${size}px Orbitron, Arial, sans-serif`;
    ctx.fillText(text, x, y);
  }

  // Background grid
  const bg = { scroll: 0, flipTimer: 0, flipX: false, flipY: false };
  function drawBackground(distance) {
    const isDark = Math.floor(distance) % 800 < 400;
    ctx.fillStyle = isDark ? DARK_GREY : LIGHT_GREY;
    ctx.fillRect(0, 0, BASE_WIDTH, BASE_HEIGHT);
    const line = isDark ? '#323232' : '#969696';
    ctx.strokeStyle = line; ctx.lineWidth = 1;
    for (let x=0;x<BASE_WIDTH;x+=50) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, BASE_HEIGHT); ctx.stroke(); }
    for (let y=0;y<BASE_HEIGHT;y+=50) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(BASE_WIDTH, y); ctx.stroke(); }
    for (let x=0;x<BASE_WIDTH;x+=100) {
      for (let y=0;y<BASE_HEIGHT;y+=100) {
        ctx.fillStyle = line; ctx.beginPath(); ctx.arc(x, y + (bg.scroll%100), 2, 0, Math.PI*2); ctx.fill();
      }
    }
  }

  // Main loop
  function tick(now) {
    requestAnimationFrame(tick);
    if (state === 'start') return; // UI only

    if (state === 'playing') {
      // Pause handling
      if (keys.has('escape')) {
        if (!paused) { paused = true; showPause(); }
      }
      if (paused) {
        if (!keys.has('escape')){} // wait for release
        if (keys.has('q')) { quitToStart(); return; }
        return;
      }

      // Shooting
      if (keys.has(' ')) {
        const b = player.shoot(now);
        if (b) bullets.push(b);
      }

      // Time-based speed scaling
      const elapsed = (now - gameStartAt) / 1000;
      const speedScale = 1.0 + (elapsed * 0.01);
      const currentSpeed = baseSpeed * speedScale * speedMultiplier;
      scrollSpeed = currentSpeed; player.speed = currentSpeed;

      // Update background
      bg.scroll = (bg.scroll + scrollSpeed/2) % BASE_HEIGHT;
      drawBackground(player.distance);

      // Input
      player.move();

      // Timers
      spawnTimer++; laserTimer++; coinTimer++;

      // Checkpoint/powerup
      const checkpointDistance = 400;
      if (Math.floor(player.distance) > lastCheckpoint && Math.floor(player.distance) % checkpointDistance === 0) {
        lastCheckpoint = Math.floor(player.distance);
        difficulty++;
        const types = ['invincibility','magnet','bullet'];
        const pos = findSafePos(30, 30, [...obstacles, ...lasers, ...powerups, ...coins]);
        if (pos) powerups.push(new PowerUp(pos.x, pos.y, types[Math.floor(Math.random()*types.length)]));
        drawText(`Checkpoint Reached! Level: ${difficulty}`, BASE_WIDTH/2 - 200, BASE_HEIGHT/2, 24, GREEN);
      }

      const expired = player.updatePowerup(now);
      if (expired) { powerupText = expired; powerupTimer = 60; if (expired.includes('Invincibility')) speedMultiplier = 1.0; if (expired.includes('Magnet')) player.magnet = false; if (expired.includes('Bullet')) player.canShoot = false; }

      if (spawnTimer > 60) {
        spawnTimer = 0;
        const pos = findSafePos(144, 144, [...obstacles, ...lasers, ...powerups, ...coins]);
        if (pos) {
          const obs = new Obstacle(pos.x, pos.y);
          obstacles.push(obs);
          if (!ensureSafePath([...obstacles, ...lasers])) obstacles.pop();
        }
        if (Math.random() < 0.1) {
          const types = ['invincibility','magnet','bullet'];
          const p = findSafePos(30, 30, [...obstacles, ...lasers, ...powerups, ...coins]);
          if (p) powerups.push(new PowerUp(p.x, p.y, types[Math.floor(Math.random()*types.length)]));
        }
      }

      // Lasers
      if (laserTimer > 180) {
        laserTimer = 0;
        for (let i=0;i<5;i++) {
          const x1 = 50 + Math.floor(Math.random()*(BASE_WIDTH-100));
          const x2 = 50 + Math.floor(Math.random()*(BASE_WIDTH-100));
          const y1 = -20; const y2 = y1 - Math.floor(Math.random()*(BASE_HEIGHT/2));
          const l = new Laser(x1, y1, x2, y2);
          const hitbox = { x: Math.min(l.x1,l.x2)-5, y: Math.min(l.y1,l.y2)-5, w: Math.abs(l.x2-l.x1)+10, h: Math.abs(l.y2-l.y1)+10 };
          const overlapped = [...obstacles, ...lasers, ...powerups, ...coins].some(o => {
            const ro = o.hitbox ? o.hitbox : (o.rect ? o.rect() : null); if (!ro) return false; const exp = { x: ro.x - 30, y: ro.y - 30, w: ro.w + 60, h: ro.h + 60 }; return rectsOverlap(exp, hitbox);
          });
          if (!overlapped && ensureSafePath([...obstacles, ...lasers, l])) { lasers.push(l); break; }
        }
      }

      // Coin lines
      if (coinTimer > 90) { coinTimer = 0; const baseX = 100 + Math.floor(Math.random()*(BASE_WIDTH-200)); spawnCoinLine(baseX, [...obstacles, ...lasers, ...powerups, ...coins], coins); }

      // Bullets
      for (let i=bullets.length-1;i>=0;i--) {
        const b = bullets[i]; b.update(); b.draw();
        for (let j=obstacles.length-1;j>=0;j--) {
          const o = obstacles[j];
          if (rectsOverlap(b.rect(), o.hitbox)) { obstacles.splice(j,1); bullets.splice(i,1); break; }
        }
        if (!b.active) bullets.splice(i,1);
      }

      // Lasers
      for (const l of lasers) { l.update(scrollSpeed); l.draw(); }

      // Obstacles
      for (const o of obstacles) { o.update(scrollSpeed); o.draw(); }

      // Coins
      for (const c of coins) {
        c.update(scrollSpeed);
        if (!c.collected && rectsOverlap(c.rect(), player.hitbox())) { c.collected = true; player.coins++; }
        if (player.magnet && !c.collected && Math.abs(c.x - (player.x + player.width/2)) < 100) {
          c.x += Math.sign((player.x + player.width/2) - c.x) * 5;
          c.y += Math.sign((player.y + player.height/2) - c.y) * 5;
        }
        c.draw();
      }

      // Powerups
      for (let i=powerups.length-1;i>=0;i--) {
        const p = powerups[i]; p.update(scrollSpeed); p.draw();
        if (rectsOverlap(p.rect(), player.hitbox())) {
          if (p.type === 'invincibility') { player.invincible = true; speedMultiplier = 3.0; powerupText = 'Invincibility Activated!'; }
          else if (p.type === 'magnet') { player.magnet = true; powerupText = 'Magnet Power Activated!'; }
          else if (p.type === 'bullet') { player.canShoot = true; powerupText = 'Bullet Power Activated!'; }
          player.powerupStart = now; powerupTimer = 60; powerups.splice(i,1);
        }
      }

      // Player and HUD
      player.draw();
      player.distance += scrollSpeed / FPS;
      drawText(`Coins: ${player.coins}`, 10, 30, 24, WHITE);
      drawText(`Distance: ${Math.floor(player.distance)}`, 10, 60, 24, WHITE);
      if (powerupText && powerupTimer-- > 0) drawText(powerupText, BASE_WIDTH/2 - 200, BASE_HEIGHT - 40, 24, GREEN);

      // Collisions causing game over
      for (const o of obstacles) {
        if (rectsOverlap(o.hitbox, player.hitbox()) && !player.invincible) {
          score = Math.floor(player.distance * Math.max(1, player.coins));
          endGame(); return;
        }
      }
      for (const l of lasers) {
        if (l.collides(player.hitbox()) && !player.invincible) {
          score = Math.floor(player.distance * Math.max(1, player.coins));
          endGame(); return;
        }
      }
    }
  }

  function endGame() {
    state = 'gameover';
    hideAllPanels();
    if (score > highScore) highScore = score;
    scoreLine.textContent = `Score: ${score}`;
    highScoreLine.textContent = `High Score: ${highScore}`;
    showGameover();
  }

  // Pause toggle and quit handling separate from main loop for responsiveness
  window.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (state === 'playing' && k === 'escape') {
      if (!paused) { paused = true; showPause(); }
      else { paused = false; hideAllPanels(); }
    }
    if (state === 'paused' && k === 'q') {
      quitToStart();
    }
  });

  // Show start at load
  showStart();
  requestAnimationFrame(tick);
})();

function hexToRgb(hex) {
  const h = hex.replace('#','');
  const bigint = parseInt(h, 16);
  if (h.length === 6) {
    const r = (bigint >> 16) & 255; const g = (bigint >> 8) & 255; const b = bigint & 255;
    return `${r},${g},${b}`;
  }
  return '0,0,0';
}


