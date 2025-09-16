import pygame
import sys
import os
import random
import math

# Initialize Pygame
pygame.init()

# Web-optimized settings
BASE_WIDTH, BASE_HEIGHT = 800, 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 10
OBSTACLE_SPEED = 3
COIN_RADIUS = 15
POWERUP_SIZE = 45

# Asset loading function
def load_image(name, scale=1):
    """Load and scale an image"""
    try:
        image = pygame.image.load(name)
        if scale != 1:
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            image = pygame.transform.scale(image, (width, height))
        return image
    except pygame.error:
        # Create a colored rectangle as fallback
        surface = pygame.Surface((32, 32))
        surface.fill(RED if "enemy" in name else YELLOW if "coin" in name else BLUE)
        return surface

def load_gif_frames(gif_path, target_width=None):
    """Load GIF frames for animation"""
    try:
        # For web, we'll create simple colored rectangles
        frames = []
        colors = [RED, GREEN, BLUE, YELLOW]
        for i in range(4):
            surface = pygame.Surface((32, 32))
            surface.fill(colors[i])
            frames.append(surface)
        return frames
    except:
        return [pygame.Surface((32, 32))]

# Animation class
class Animation:
    def __init__(self, frames, frame_duration=100):
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now
    
    def get_current_frame(self):
        return self.frames[self.current_frame]

# Background class
class Background:
    def __init__(self):
        self.stars = []
        for _ in range(100):
            x = random.randint(0, BASE_WIDTH)
            y = random.randint(0, BASE_HEIGHT)
            self.stars.append((x, y))
    
    def draw(self, surface, scroll_speed=0):
        surface.fill(BLACK)
        for x, y in self.stars:
            pygame.draw.circle(surface, WHITE, (x, y - scroll_speed), 1)

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.animation = Animation(load_gif_frames("robo.gif"))
    
    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        # Keep player on screen
        self.x = max(0, min(self.x, BASE_WIDTH - self.width))
        self.y = max(0, min(self.y, BASE_HEIGHT - self.height))
        
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

# Bullet class
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = BULLET_SPEED
        self.active = True
    
    def update(self):
        self.y -= self.speed
        if self.y < 0:
            self.active = False
    
    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)

# Obstacle class
class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = OBSTACLE_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.animation = Animation(load_gif_frames("enemy.gif"))
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
    
    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)

# Coin class
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = COIN_RADIUS
        self.collected = False
    
    def draw(self, surface):
        if not self.collected:
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)

# PowerUp class
class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type
        self.size = POWERUP_SIZE
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.collected = False
    
    def draw(self, surface):
        if not self.collected:
            color = BLUE if self.power_type == "invincibility" else GREEN
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 2)

# Game state
class GameState:
    START_SCREEN = "start"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

def start_screen(surface, font_large, font_small):
    surface.fill(BLACK)
    
    # Title
    title_text = font_large.render("RoboRun", True, GREEN)
    title_rect = title_text.get_rect(center=(BASE_WIDTH//2, BASE_HEIGHT//2 - 100))
    surface.blit(title_text, title_rect)
    
    # Controls
    controls_bg = pygame.Rect(50, BASE_HEIGHT//2 - 50, 300, 150)
    pygame.draw.rect(surface, DARK_GRAY, controls_bg)
    pygame.draw.rect(surface, WHITE, controls_bg, 2)
    
    controls_text = font_small.render("Controls:", True, WHITE)
    surface.blit(controls_text, (60, BASE_HEIGHT//2 - 40))
    
    controls = [
        "Arrow Keys or WASD - Move",
        "Space - Shoot",
        "R - Start/Restart",
        "ESC - Pause"
    ]
    
    for i, control in enumerate(controls):
        text = font_small.render(control, True, WHITE)
        surface.blit(text, (60, BASE_HEIGHT//2 - 20 + i * 20))
    
    # Start instruction
    start_text = font_small.render("Press R to Start!", True, YELLOW)
    start_rect = start_text.get_rect(center=(BASE_WIDTH//2, BASE_HEIGHT//2 + 100))
    surface.blit(start_text, start_rect)

def game_over_screen(surface, font_large, font_small, score):
    surface.fill(BLACK)
    
    game_over_text = font_large.render("Game Over!", True, RED)
    game_over_rect = game_over_text.get_rect(center=(BASE_WIDTH//2, BASE_HEIGHT//2 - 50))
    surface.blit(game_over_text, game_over_rect)
    
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(BASE_WIDTH//2, BASE_HEIGHT//2))
    surface.blit(score_text, score_rect)
    
    restart_text = font_small.render("Press R to Restart", True, YELLOW)
    restart_rect = restart_text.get_rect(center=(BASE_WIDTH//2, BASE_HEIGHT//2 + 50))
    surface.blit(restart_text, restart_rect)

def main():
    # Set up display
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT))
    pygame.display.set_caption("RoboRun")
    clock = pygame.time.Clock()
    
    # Fonts
    font_large = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 24)
    
    # Game objects
    background = Background()
    player = Player(BASE_WIDTH//2, BASE_HEIGHT - 100)
    bullets = []
    obstacles = []
    coins = []
    powerups = []
    
    # Game state
    game_state = GameState.START_SCREEN
    score = 0
    distance_travelled = 0
    
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if game_state == GameState.START_SCREEN:
                        game_state = GameState.PLAYING
                    elif game_state == GameState.GAME_OVER:
                        # Reset game
                        game_state = GameState.PLAYING
                        score = 0
                        distance_travelled = 0
                        bullets = []
                        obstacles = []
                        coins = []
                        powerups = []
                        player = Player(BASE_WIDTH//2, BASE_HEIGHT - 100)
                elif event.key == pygame.K_ESCAPE:
                    if game_state == GameState.PLAYING:
                        game_state = GameState.PAUSED
                    elif game_state == GameState.PAUSED:
                        game_state = GameState.PLAYING
                elif event.key == pygame.K_SPACE and game_state == GameState.PLAYING:
                    bullets.append(Bullet(player.x + player.width//2, player.y))
        
        # Update game
        if game_state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            player.move(keys)
            
            # Update bullets
            for bullet in bullets[:]:
                bullet.update()
                if not bullet.active:
                    bullets.remove(bullet)
            
            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle.update()
                if obstacle.y > BASE_HEIGHT:
                    obstacles.remove(obstacle)
            
            # Update coins
            for coin in coins:
                coin.draw(screen)
            
            # Update powerups
            for powerup in powerups:
                powerup.draw(screen)
            
            # Spawn obstacles
            if random.randint(1, 60) == 1:
                obstacles.append(Obstacle(random.randint(0, BASE_WIDTH - 30), -30))
            
            # Spawn coins
            if random.randint(1, 120) == 1:
                coins.append(Coin(random.randint(50, BASE_WIDTH - 50), -30))
            
            # Collision detection
            for bullet in bullets[:]:
                for obstacle in obstacles[:]:
                    if (abs(bullet.x - obstacle.x) < 20 and 
                        abs(bullet.y - obstacle.y) < 20):
                        bullets.remove(bullet)
                        obstacles.remove(obstacle)
                        score += 10
            
            # Player collision with obstacles
            for obstacle in obstacles:
                if player.rect.colliderect(obstacle.rect):
                    game_state = GameState.GAME_OVER
            
            # Player collision with coins
            for coin in coins[:]:
                if (abs(player.x - coin.x) < 30 and 
                    abs(player.y - coin.y) < 30):
                    coins.remove(coin)
                    score += 5
        
        # Draw everything
        background.draw(screen, distance_travelled)
        
        if game_state == GameState.START_SCREEN:
            start_screen(screen, font_large, font_small)
        elif game_state == GameState.PLAYING:
            player.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)
            for coin in coins:
                coin.draw(screen)
            for powerup in powerups:
                powerup.draw(screen)
            
            # Draw score
            score_text = font_small.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
        elif game_state == GameState.PAUSED:
            pause_text = font_large.render("PAUSED", True, YELLOW)
            pause_rect = pause_text.get_rect(center=(BASE_WIDTH//2, BASE_HEIGHT//2))
            screen.blit(pause_text, pause_rect)
        elif game_state == GameState.GAME_OVER:
            game_over_screen(screen, font_large, font_small, score)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()