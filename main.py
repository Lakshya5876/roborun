import pygame
import random
import sys
import math
import os
from PIL import Image, ImageSequence

# Use the current working directory for asset loading
ASSET_DIR = os.getcwd()

pygame.init()

# Base virtual resolution - all game logic uses these dimensions
# Optimized for sleek, clean appearance
BASE_WIDTH, BASE_HEIGHT = 960, 720
FPS = 60

# Get actual screen resolution
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h

# For responsive scaling, we'll calculate scaling factors
SCALE_X = SCREEN_WIDTH / BASE_WIDTH
SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT

# Use the smaller scale factor to maintain aspect ratio and prevent stretching
SCALE = min(SCALE_X, SCALE_Y)

# Calculate actual window size (maintain aspect ratio)
WINDOW_WIDTH = int(BASE_WIDTH * SCALE)
WINDOW_HEIGHT = int(BASE_HEIGHT * SCALE)

# Center the game in the window
LETTERBOX_X = (SCREEN_WIDTH - WINDOW_WIDTH) // 2
LETTERBOX_Y = (SCREEN_HEIGHT - WINDOW_HEIGHT) // 2

# Use base resolution for all game logic
WIDTH, HEIGHT = BASE_WIDTH, BASE_HEIGHT

PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50
OBSTACLE_MIN_SIZE = 30
OBSTACLE_MAX_SIZE = 70
COIN_RADIUS = 10
CHECKPOINT_DISTANCE = 400
MIN_GAP_SIZE = 120

WHITE = (255,255,255)
RED = (255,0,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
MAGENTA = (255,0,255)
GREY = (100,100,100)
ORANGE = (255,165,0)
DARK_GREY = (30, 30, 30)
LIGHT_GREY = (200, 200, 200)

# Create the display window (resizable for responsive design)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("RoboRun - Web Edition")
clock = pygame.time.Clock()

# Create virtual surface for rendering at base resolution
virtual_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

def scale_coords_to_virtual(screen_x, screen_y):
    """Convert screen coordinates to virtual coordinates
    Use this function when handling mouse input to convert screen coordinates
    to the virtual coordinate system used by the game logic.
    """
    # Remove letterbox offset
    virtual_x = (screen_x - LETTERBOX_X) / SCALE
    virtual_y = (screen_y - LETTERBOX_Y) / SCALE
    return int(virtual_x), int(virtual_y)

def scale_coords_to_screen(virtual_x, virtual_y):
    """Convert virtual coordinates to screen coordinates"""
    screen_x = int(virtual_x * SCALE + LETTERBOX_X)
    screen_y = int(virtual_y * SCALE + LETTERBOX_Y)
    return screen_x, screen_y

def render_to_screen():
    """Scale the virtual surface to screen with responsive scaling"""
    # Clear the screen with a subtle pattern
    screen.fill((20, 20, 20))  # Dark gray instead of pure black
    
    # Add subtle pattern to letterbox areas
    if LETTERBOX_X > 0 or LETTERBOX_Y > 0:
        # Draw subtle diagonal lines in letterbox areas
        for x in range(0, SCREEN_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                if (x + y) % 80 == 0:
                    pygame.draw.circle(screen, (30, 30, 30), (x, y), 1)
    
    # Scale the virtual surface to maintain aspect ratio
    scaled_surface = pygame.transform.smoothscale(virtual_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Center the scaled surface on the screen
    screen.blit(scaled_surface, (LETTERBOX_X, LETTERBOX_Y))

def load_image(name, scale=1):
    try:
        image = pygame.image.load(name)
        if scale != 1:
            # Scale based on the virtual resolution scaling
            final_scale = scale * SCALE
            image = pygame.transform.scale(image, 
                (int(image.get_width() * final_scale), int(image.get_height() * final_scale)))
        return image
    except Exception as e:
        print(f"Error loading image {name}: {e}")
        return None

def load_gif_frames(gif_path, target_width=None):
    try:
        gif = Image.open(gif_path)
        frames = []
        for frame in ImageSequence.Iterator(gif):
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            frame_surface = pygame.image.fromstring(
                frame.tobytes(), frame.size, frame.mode)
            
            if target_width:
                # Scale based on the virtual resolution scaling
                scale = (target_width * SCALE) / frame_surface.get_width()
                new_size = (int(frame_surface.get_width() * scale),
                          int(frame_surface.get_height() * scale))
                frame_surface = pygame.transform.scale(frame_surface, new_size)
            
            frames.append(frame_surface)
        return frames
    except Exception as e:
        print(f"Error loading GIF {gif_path}: {e}")
        return None

try:
    font = pygame.font.Font(os.path.join(ASSET_DIR, "assets/fonts/space_font.ttf"), int(36 * SCALE))
    small_font = pygame.font.Font(os.path.join(ASSET_DIR, "assets/fonts/space_font.ttf"), int(24 * SCALE))
except:
    font = pygame.font.SysFont(None, int(36 * SCALE))
    small_font = pygame.font.SysFont(None, int(24 * SCALE))

try:
    player_image = pygame.image.load(os.path.join(ASSET_DIR, "robo.gif")).convert_alpha()
    player_image = pygame.transform.scale(player_image, (int(PLAYER_WIDTH * SCALE), int(PLAYER_HEIGHT * SCALE)))
    enemy_image = pygame.image.load(os.path.join(ASSET_DIR, "enemy.gif")).convert_alpha()
    coin_sprite = load_image(os.path.join(ASSET_DIR, "coin.png"), 0.3)
    powerup_sprites = {
        'invincibility': load_image(os.path.join(ASSET_DIR, "invincibility.png"), 0.3),
        'magnet': load_image(os.path.join(ASSET_DIR, "magnet.png"), 0.3)
    }
except:
    player_image = None
    enemy_image = None
    coin_sprite = None
    powerup_sprites = None

high_score = 0

def check_overlap(rect, game_objects, buffer=20):
    expanded_rect = pygame.Rect(rect.x - buffer, rect.y - buffer, 
                              rect.width + 2*buffer, rect.height + 2*buffer)
    
    for obj in game_objects:
        if hasattr(obj, 'rect'):
            if expanded_rect.colliderect(obj.rect):
                return True
        elif hasattr(obj, 'box1') and hasattr(obj, 'box2'):
            if expanded_rect.colliderect(obj.box1) or expanded_rect.colliderect(obj.box2):
                return True
        elif hasattr(obj, 'x') and hasattr(obj, 'y'):
            coin_radius = getattr(obj, 'radius', COIN_RADIUS)
            coin_rect = pygame.Rect(obj.x - coin_radius - buffer, obj.y - coin_radius - buffer, 
                                  (coin_radius*2) + 2*buffer, (coin_radius*2) + 2*buffer)
            if expanded_rect.colliderect(coin_rect):
                return True
    return False

def find_safe_spawn_position(width, height, game_objects, max_attempts=10):
    for _ in range(max_attempts):
        x = random.randint(width, WIDTH - width)
        y = -height
        rect = pygame.Rect(x, y, width, height)
        if not check_overlap(rect, game_objects, buffer=30):
            return x, y
    return None, None

def ensure_safe_path(game_objects):
    lane_width = WIDTH // 3
    lanes = [0, lane_width, lane_width * 2]
    
    for lane in lanes:
        lane_rect = pygame.Rect(lane, 0, lane_width, HEIGHT)
        has_obstacle = False
        
        for obj in game_objects:
            if hasattr(obj, 'rect') and lane_rect.colliderect(obj.rect):
                has_obstacle = True
                break
        
        if not has_obstacle:
            return True
    
    return False

class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, x, y, width, height, scale=1):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        return image

class Animation:
    def __init__(self, frames, speed=0.1):
        self.frames = frames
        self.speed = speed
        self.index = 0
        self.timer = 0

    def update(self):
        self.timer += self.speed
        if self.timer >= 1:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)

    def get_current_frame(self):
        return self.frames[int(self.index)]

class Background:
    def __init__(self):
        self.bg_image = pygame.Surface((WIDTH, HEIGHT))
        self.scroll = 0
        self.flip_timer = 0
        self.flip_x = False
        self.flip_y = False

    def update(self, speed, distance):
        self.scroll = (self.scroll + speed/2) % HEIGHT
        self.flip_timer += 1
        
        if self.flip_timer >= 120:
            self.flip_timer = 0
            self.flip_x = random.random() < 0.5
            self.flip_y = random.random() < 0.5

    def draw(self, surface, distance):
        is_dark = (int(distance) // 400) % 2 == 0
        bg_color = DARK_GREY if is_dark else LIGHT_GREY
        line_color = (50, 50, 50) if is_dark else (150, 150, 150)
        
        self.bg_image.fill(bg_color)
        
        for x in range(0, WIDTH, 50):
            pygame.draw.line(self.bg_image, line_color, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(self.bg_image, line_color, (0, y), (WIDTH, y))
            
        for x in range(0, WIDTH, 100):
            for y in range(0, HEIGHT, 100):
                pygame.draw.circle(self.bg_image, line_color, (x, y), 2)
                if (x // 100 + y // 100) % 2 == 0:
                    pygame.draw.line(self.bg_image, line_color, (x-10, y-10), (x+10, y+10), 1)
                    pygame.draw.line(self.bg_image, line_color, (x-10, y+10), (x+10, y-10), 1)
        
        surface.blit(self.bg_image, (0, self.scroll))
        surface.blit(self.bg_image, (0, self.scroll - HEIGHT))

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.radius = int(5 * SCALE)
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        self.trail_particles = []
        self.active = True

    def update(self):
        self.y -= self.speed
        self.rect.y = self.y - self.radius
        
        # Add trail particles
        if random.random() < 0.3:
            self.trail_particles.append({
                'x': self.x + random.randint(-2, 2),
                'y': self.y + random.randint(-2, 2),
                'life': 10
            })
        
        # Update trail particles
        for particle in self.trail_particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.trail_particles.remove(particle)

    def draw(self, surface):
        # Draw trail particles
        for particle in self.trail_particles:
            alpha = int(255 * (particle['life'] / 10))
            color = (100, 200, 255, alpha)
            pygame.draw.circle(surface, color, (int(particle['x']), int(particle['y'])), 2)
        
        # Draw bullet
        pygame.draw.circle(surface, BLUE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius - 2)

class Player:
    def __init__(self):
        self.target_width = 120
        
        self.animation = Animation(load_gif_frames(os.path.join(ASSET_DIR, "robo.gif"), self.target_width))
        if self.animation and self.animation.frames:
            first_frame = self.animation.frames[0]
            self.width = first_frame.get_width()
            self.height = first_frame.get_height()
        else:
            self.width = self.target_width
            self.height = self.target_width
            print("Warning: Using fallback player dimensions")
        
        self.rect = pygame.Rect(WIDTH//2 - self.width//2, HEIGHT-100, 
                              self.width, self.height)
        self.speed = 5
        self.base_speed = 5
        self.invincible = False
        self.magnet = False
        self.can_shoot = False
        self.powerup_timer = 0
        self.coins_collected = 0
        self.distance_travelled = 0
        self.hit_timer = 0
        self.last_shot_time = 0
        self.shoot_cooldown = 300  # milliseconds

    def get_hitbox(self):
        shrink = self.width // 5
        return pygame.Rect(self.rect.x + shrink, self.rect.y + shrink,
                          self.width - 2*shrink, self.height - 2*shrink)

    def move(self, keys):
        # Arrow keys and WASD controls
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x = max(0, self.rect.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x = min(WIDTH - self.width, self.rect.x + self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y = max(0, self.rect.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y = min(HEIGHT - self.height, self.rect.y + self.speed)

    def draw(self, surface):
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer % 4 < 2:
                return

        if self.animation and self.animation.frames:
            self.animation.update()
            surface.blit(self.animation.get_current_frame(), self.rect.topleft)
        else:
            color = GREEN if self.invincible else BLUE
            pygame.draw.rect(surface, color, self.rect)

    def update_powerup(self):
        if self.invincible or self.magnet or self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.powerup_timer > 10000:  # 10 seconds
                if self.invincible:
                    self.invincible = False
                    return "Invincibility Expired!"
                elif self.magnet:
                    self.magnet = False
                    return "Magnet Power Expired!"
                elif self.can_shoot:
                    self.can_shoot = False
                    return "Bullet Power Expired!"
        return None

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if self.can_shoot and current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            return Bullet(self.rect.centerx, self.rect.top)
        return None

class Obstacle:
    def __init__(self, x, y, type='drone'):
        self.type = type
        if type == 'drone':
            self.target_width = 144
            
            self.animation = Animation(load_gif_frames(os.path.join(ASSET_DIR, "enemy.gif"), self.target_width))
            if self.animation and self.animation.frames:
                first_frame = self.animation.frames[0]
                self.width = first_frame.get_width()
                self.height = first_frame.get_height()
            else:
                self.width = self.target_width
                self.height = self.target_width
                print("Warning: Using fallback enemy dimensions")
            
            self.rect = pygame.Rect(x, y, self.width, self.height)
            self.hitbox = pygame.Rect(x + self.width//4, y + self.height//4, 
                                    self.width//2, self.height//2)
        else:
            self.animation = None
            self.width = int(45 * SCALE)
            self.height = int(45 * SCALE)
            self.rect = pygame.Rect(x, y, self.width, self.height)
            self.hitbox = self.rect

    def update(self, speed):
        self.rect.y += speed
        if self.type == 'drone':
            self.hitbox.x = self.rect.x + self.width//4
            self.hitbox.y = self.rect.y + self.height//4

    def draw(self, surface):
        if self.type == 'drone' and self.animation and self.animation.frames:
            self.animation.update()
            surface.blit(self.animation.get_current_frame(), self.rect.topleft)
        else:
            if self.type == 'drone':
                pygame.draw.rect(surface, MAGENTA, self.rect)

class Laser:
    def __init__(self, x1, y1, x2, y2):
        max_length = WIDTH * 0.7  # 70% of screen width
        
        # Calculate current length
        current_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # If length exceeds max_length, scale down the endpoint
        if current_length > max_length:
            scale = max_length / current_length
            x2 = x1 + (x2 - x1) * scale
            y2 = y1 + (y2 - y1) * scale
        
        self.box1 = pygame.Rect(x1 - 10, y1 - 10, 20, 20)
        self.box2 = pygame.Rect(x2 - 10, y2 - 10, 20, 20)
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.pulse_timer = 0
        self.pulse_speed = 0.2
        self.hitbox = pygame.Rect(min(x1, x2) - 5, min(y1, y2) - 5,
                                abs(x2 - x1) + 10, abs(y2 - y1) + 10)

    def update(self, speed):
        self.y1 += speed
        self.y2 += speed
        self.box1.y = self.y1 - 10
        self.box2.y = self.y2 - 10
        self.hitbox.y += speed
        self.pulse_timer += self.pulse_speed

    def draw(self, surface):
        pulse = abs(math.sin(self.pulse_timer)) * 0.3 + 0.7
        
        for box in [self.box1, self.box2]:
            glow_surface = pygame.Surface((box.width + 20, box.height + 20), pygame.SRCALPHA)
            glow_color = (255, 0, 0, int(100 * pulse))
            pygame.draw.rect(glow_surface, glow_color, 
                           (10, 10, box.width, box.height),
                           border_radius=10)
            surface.blit(glow_surface, 
                       (box.x - 10, box.y - 10))
            
            pygame.draw.rect(surface, RED, box, border_radius=10)
            
            highlight_rect = box.inflate(-4, -4)
            highlight_color = (255, 100, 100)
            pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=8)
        
        points = [(self.x1, self.y1), (self.x2, self.y2)]
        for width in range(8, 3, -1):
            alpha = int(100 * pulse * (width / 8))
            color = (255, 0, 0, alpha)
            pygame.draw.line(surface, color, points[0], points[1], width)
        
        pygame.draw.line(surface, RED, points[0], points[1], 4)
        
        for _ in range(3):
            t = random.random()
            x = self.x1 + (self.x2 - self.x1) * t
            y = self.y1 + (self.y2 - self.y1) * t
            particle_radius = random.randint(2, 4)
            pygame.draw.circle(surface, (255, 200, 200), (int(x), int(y)), particle_radius)

    def collides_with(self, rect):
        line_rect = pygame.Rect(min(self.x1, self.x2) - 5, min(self.y1, self.y2) - 5,
                              abs(self.x2 - self.x1) + 10, abs(self.y2 - self.y1) + 10)
        if not line_rect.colliderect(rect):
            return False
            
        points = [
            (rect.left, rect.top), (rect.right, rect.top),
            (rect.left, rect.bottom), (rect.right, rect.bottom),
            (rect.centerx, rect.centery)
        ]
        
        for px, py in points:
            line_length = math.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)
            if line_length == 0:
                continue
                
            t = max(0, min(1, ((px - self.x1) * (self.x2 - self.x1) + 
                              (py - self.y1) * (self.y2 - self.y1)) / (line_length**2)))
            closest_x = self.x1 + t * (self.x2 - self.x1)
            closest_y = self.y1 + t * (self.y2 - self.y1)
            
            distance = math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
            if distance < 6:
                return True
        return False

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.radius = int(COIN_RADIUS * SCALE)
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius*2, self.radius*2)
        self.sprite = coin_sprite

    def update(self, speed):
        self.y += speed
        self.rect.y = self.y - self.radius

    def draw(self, surface):
        if not self.collected:
            if self.sprite:
                surface.blit(self.sprite, (self.x - self.sprite.get_width()//2, 
                                        self.y - self.sprite.get_height()//2))
            else:
                pygame.draw.circle(surface, YELLOW, (self.x, self.y), self.radius)

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.lifetime = 30
        self.create_particles()

    def create_particles(self):
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'life': self.lifetime,
                'color': (random.randint(200, 255), random.randint(100, 200), 0)
            })

    def update(self):
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            particle['dy'] += 0.1  # gravity effect

    def draw(self, surface):
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / self.lifetime))
                color = (*particle['color'], alpha)
                pygame.draw.circle(surface, color, 
                                 (int(particle['x']), int(particle['y'])), 
                                 int(particle['life'] / 10) + 1)

class PowerUp:
    def __init__(self, x, y, type='invincibility'):
        powerup_size = int(45 * SCALE)
        self.rect = pygame.Rect(x, y, powerup_size, powerup_size)
        self.type = type
        self.active = False
        self.animation = None
        self.color = GREEN if type == 'invincibility' else (ORANGE if type == 'magnet' else BLUE)
        self.pulse_timer = 0
        self.pulse_speed = 0.1
        self.rotation = 0
        self.rotation_speed = 2

    def update(self, speed):
        self.rect.y += speed
        if self.animation:
            self.animation.update()
        
        self.pulse_timer += self.pulse_speed
        self.rotation = (self.rotation + self.rotation_speed) % 360

    def draw(self, surface):
        pulse = abs(math.sin(self.pulse_timer)) * 0.3 + 0.7
        
        glow_radius = int(30 * pulse)
        glow_surface = pygame.Surface((self.rect.width + glow_radius*2, 
                                     self.rect.height + glow_radius*2), 
                                    pygame.SRCALPHA)
        glow_color = (*self.color, int(100 * pulse))
        pygame.draw.rect(glow_surface, glow_color, 
                        (glow_radius, glow_radius, self.rect.width, self.rect.height),
                        border_radius=12)
        surface.blit(glow_surface, 
                   (self.rect.x - glow_radius, self.rect.y - glow_radius))
        
        pygame.draw.rect(surface, self.color, self.rect, border_radius=12)
        
        highlight_rect = self.rect.inflate(-6, -6)
        highlight_color = tuple(min(c + 50, 255) for c in self.color)
        pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=9)
        
        border_points = []
        center = self.rect.center
        radius = max(self.rect.width, self.rect.height) // 2 + 3
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            border_points.append((x, y))
        
        pygame.draw.lines(surface, WHITE, True, border_points, 3)
        
        if self.type == 'invincibility':
            shield_points = [
                (self.rect.centerx, self.rect.top + 8),
                (self.rect.right - 8, self.rect.centery),
                (self.rect.centerx, self.rect.bottom - 8),
                (self.rect.left + 8, self.rect.centery)
            ]
            pygame.draw.polygon(surface, WHITE, shield_points, 3)
        elif self.type == 'magnet':
            magnet_width = 12
            magnet_height = 18
            magnet_x = self.rect.centerx - magnet_width//2
            magnet_y = self.rect.centery - magnet_height//2
            pygame.draw.rect(surface, WHITE, 
                           (magnet_x, magnet_y, magnet_width, magnet_height), 3)
            for i in range(3):
                y = magnet_y + magnet_height + i * 6
                pygame.draw.line(surface, WHITE,
                               (magnet_x - 6, y),
                               (magnet_x + magnet_width + 6, y), 2)
        elif self.type == 'bullet':
            # Draw bullet icon
            bullet_length = 20
            bullet_width = 8
            pygame.draw.rect(surface, WHITE,
                           (self.rect.centerx - bullet_width//2,
                            self.rect.centery - bullet_length//2,
                            bullet_width, bullet_length), 0)
            pygame.draw.circle(surface, WHITE,
                             (self.rect.centerx, self.rect.centery - bullet_length//2),
                             bullet_width//2)

def display_text(text, size, x, y, color=WHITE, surface=None):
    if surface is None:
        surface = virtual_surface
    font_to_use = font if size > 24 else small_font
    label = font_to_use.render(text, True, color)
    surface.blit(label, (x, y))

def start_screen():
    """Display the start screen with title, controls, and instructions"""
    while True:
        virtual_surface.fill(BLACK)
        
        # Title
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("RoboRun", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        virtual_surface.blit(title_text, title_rect)
        
        # Controls
        controls_font = pygame.font.Font(None, 36)
        controls_text = [
            "Controls:",
            "Arrow Keys or WASD - Move",
            "SPACE - Shoot (when powerup active)",
            "ESC - Pause"
        ]
        
        y_offset = HEIGHT//2 - 60
        for i, text in enumerate(controls_text):
            color = YELLOW if i == 0 else WHITE
            font_size = 36 if i == 0 else 28
            text_surface = pygame.font.Font(None, font_size).render(text, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH//2, y_offset + i * 35))
            virtual_surface.blit(text_surface, text_rect)
        
        # Instructions
        instruction_font = pygame.font.Font(None, 48)
        instruction_text = instruction_font.render("Press R to Play", True, GREEN)
        instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 100))
        virtual_surface.blit(instruction_text, instruction_rect)
        
        # High score
        if high_score > 0:
            high_score_text = pygame.font.Font(None, 32).render(f"High Score: {high_score}", True, GREY)
            high_score_rect = high_score_text.get_rect(center=(WIDTH//2, HEIGHT - 50))
            virtual_surface.blit(high_score_text, high_score_rect)
        
        render_to_screen()
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def game_over_menu(score):
    global high_score
    if score > high_score:
        high_score = score
    while True:
        virtual_surface.fill(BLACK)
        display_text("Game Over", 64, WIDTH//3, HEIGHT//4, RED)
        display_text(f"Score: {score}", 36, WIDTH//3, HEIGHT//3)
        display_text(f"High Score: {high_score}", 36, WIDTH//3, HEIGHT//3 + 40)
        display_text("Press R to Restart or Q to Quit", 32, WIDTH//4, HEIGHT//2)
        render_to_screen()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def spawn_coin_line(base_x, obstacles, lasers, powerups, coins):
    coin_spacing = 50
    coin_line_length = 5
    vertical_spacing = 40
    
    for i in range(coin_line_length):
        attempts = 0
        while attempts < 5:
            cx = base_x + random.randint(-10, 10)
            cy = -i * vertical_spacing
            # Create a temporary coin to get the scaled radius
            temp_coin = Coin(cx, cy)
            coin_rect = pygame.Rect(cx - temp_coin.radius, cy - temp_coin.radius, 
                                  temp_coin.radius*2, temp_coin.radius*2)
            if not check_overlap(coin_rect, obstacles + lasers + powerups + coins, buffer=30):
                coins.append(temp_coin)
                break
            attempts += 1

def game_loop():
    show_start_screen = True
    
    while True:
        # Show start screen only on first run or when returning from game over
        if show_start_screen:
            start_screen()
            show_start_screen = False
        
        player = Player()
        obstacles = []
        lasers = []
        coins = []
        powerups = []
        bullets = []
        explosions = []
        base_speed = 5  # Initial base speed
        scroll_speed = base_speed
        spawn_timer = 0
        laser_timer = 0
        coin_line_timer = 0
        running = True
        paused = False
        last_checkpoint = 0
        difficulty_level = 1
        background = Background()
        screen_shake = 0
        powerup_text = None
        powerup_text_timer = 0
        game_start_time = pygame.time.get_ticks()
        speed_multiplier = 1.0  # Base speed multiplier

        while running:
            clock.tick(FPS)
            virtual_surface.fill(BLACK)
            
            # Calculate time-based speed scaling
            current_time = pygame.time.get_ticks()
            time_elapsed = (current_time - game_start_time) / 1000.0  # Convert to seconds
            speed_scale = 1.0 + (time_elapsed * 0.01)  # Increase speed by 1% every second
            current_speed = base_speed * speed_scale * speed_multiplier
            
            # Update scroll speed based on current game speed
            scroll_speed = current_speed
            player.speed = current_speed  # Player speed matches game speed
            
            background.update(scroll_speed, player.distance_travelled)
            background.draw(virtual_surface, player.distance_travelled)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resizing for responsive design
                    global SCREEN_WIDTH, SCREEN_HEIGHT, SCALE, WINDOW_WIDTH, WINDOW_HEIGHT, LETTERBOX_X, LETTERBOX_Y
                    SCREEN_WIDTH = event.w
                    SCREEN_HEIGHT = event.h
                    SCALE_X = SCREEN_WIDTH / BASE_WIDTH
                    SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT
                    SCALE = min(SCALE_X, SCALE_Y)
                    WINDOW_WIDTH = int(BASE_WIDTH * SCALE)
                    WINDOW_HEIGHT = int(BASE_HEIGHT * SCALE)
                    LETTERBOX_X = (SCREEN_WIDTH - WINDOW_WIDTH) // 2
                    LETTERBOX_Y = (SCREEN_HEIGHT - WINDOW_HEIGHT) // 2
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = not paused
                    elif event.key == pygame.K_q and paused:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_SPACE and not paused:
                        bullet = player.shoot()
                        if bullet:
                            bullets.append(bullet)

            if paused:
                # Draw pause overlay
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                virtual_surface.blit(overlay, (0, 0))
                
                pause_text = font.render("Game Paused", True, WHITE)
                resume_text = small_font.render("Press ESC to resume", True, WHITE)
                quit_text = small_font.render("Press Q to quit", True, RED)
                virtual_surface.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 30))
                virtual_surface.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2 + 20))
                virtual_surface.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 50))
                render_to_screen()
                pygame.display.flip()
                continue

            player.move(keys)

            spawn_timer += 1
            laser_timer += 1
            coin_line_timer += 1

            if int(player.distance_travelled) % CHECKPOINT_DISTANCE == 0 and int(player.distance_travelled) > last_checkpoint:
                last_checkpoint = int(player.distance_travelled)
                difficulty_level += 1
                p_type = random.choice(['invincibility', 'magnet', 'bullet'])
                px, py = find_safe_spawn_position(30, 30, obstacles + lasers + powerups + coins)
                if px is not None:
                    powerups.append(PowerUp(px, py, p_type))
                checkpoint_message = font.render(f"Checkpoint Reached! Level: {difficulty_level}", True, GREEN)
                virtual_surface.blit(checkpoint_message, (WIDTH//2 - checkpoint_message.get_width()//2, HEIGHT//2))
                render_to_screen()
                pygame.display.flip()
                pygame.time.wait(1000)

            expired_text = player.update_powerup()
            if expired_text:
                powerup_text = expired_text
                powerup_text_timer = 60
                if "Invincibility" in expired_text:
                    speed_multiplier = 1.0  # Reset speed multiplier when invincibility expires
                elif "Magnet" in expired_text:
                    player.magnet = False
                elif "Bullet" in expired_text:
                    player.can_shoot = False

            if spawn_timer > 60:
                spawn_timer = 0
                x, y = find_safe_spawn_position(144, 144, obstacles + lasers + powerups + coins)
                if x is not None:
                    new_obstacle = Obstacle(x, y, 'drone')
                    obstacles.append(new_obstacle)
                    if not ensure_safe_path(obstacles + lasers):
                        obstacles.pop()

                if random.random() < 0.1:
                    p_type = random.choice(['invincibility', 'magnet', 'bullet'])
                    px, py = find_safe_spawn_position(30, 30, obstacles + lasers + powerups + coins)
                    if px is not None:
                        powerups.append(PowerUp(px, py, p_type))

            # Update and draw bullets
            for bullet in bullets[:]:
                bullet.update()
                bullet.draw(virtual_surface)
                
                # Check for bullet collisions with obstacles
                for obstacle in obstacles[:]:
                    if bullet.rect.colliderect(obstacle.hitbox):
                        explosions.append(Explosion(obstacle.rect.centerx, obstacle.rect.centery))
                        obstacles.remove(obstacle)
                        bullets.remove(bullet)
                        break
                
                # Remove bullets that are off screen
                if bullet.y < -bullet.radius:
                    bullets.remove(bullet)

            # Update and draw explosions
            for explosion in explosions[:]:
                explosion.update()
                explosion.draw(virtual_surface)
                if explosion.particles[0]['life'] <= 0:
                    explosions.remove(explosion)

            if laser_timer > 180:
                laser_timer = 0
                for _ in range(5):
                    x1 = random.randint(50, WIDTH - 50)
                    x2 = random.randint(50, WIDTH - 50)
                    y1 = -20
                    y2 = y1 - random.randint(60, HEIGHT//2)
                    new_laser = Laser(x1, y1, x2, y2)
                    if not check_overlap(new_laser.hitbox, obstacles + lasers + powerups + coins, buffer=30):
                        if ensure_safe_path(obstacles + lasers + [new_laser]):
                            lasers.append(new_laser)
                            break

            if coin_line_timer > 90:
                coin_line_timer = 0
                base_x = random.randint(100, WIDTH - 100)
                spawn_coin_line(base_x, obstacles, lasers, powerups, coins)

            player.distance_travelled += scroll_speed / FPS

            if screen_shake > 0:
                screen_shake -= 1
                shake_offset = random.randint(-5, 5)
                virtual_surface.blit(virtual_surface, (shake_offset, 0))

            for obs in obstacles:
                obs.update(scroll_speed)
                obs.draw(virtual_surface)
                if obs.hitbox.colliderect(player.get_hitbox()) and not player.invincible:
                    print("Enemy collision detected!")
                    player.hit_timer = 30
                    screen_shake = 10
                    score = int(player.distance_travelled * player.coins_collected)
                    result = game_over_menu(score)
                    if result == "restart":
                        running = False
                        break
                    else:
                        running = False
                        break

            for laser in lasers:
                laser.update(scroll_speed)
                laser.draw(virtual_surface)
                if laser.collides_with(player.get_hitbox()) and not player.invincible:
                    print("Laser collision detected!")
                    player.hit_timer = 30
                    screen_shake = 10
                    score = int(player.distance_travelled * player.coins_collected)
                    result = game_over_menu(score)
                    if result == "restart":
                        running = False
                        break
                    else:
                        running = False
                        break

            for coin in coins:
                coin.update(scroll_speed)
                if not coin.collected and coin.rect.colliderect(player.get_hitbox()):
                    print("Coin collected!")
                    coin.collected = True
                    player.coins_collected += 1
                if player.magnet and not coin.collected:
                    if abs(coin.x - player.rect.centerx) < 100:
                        coin.x += (player.rect.centerx - coin.x) // 5
                        coin.y += (player.rect.centery - coin.y) // 5
                        coin.rect.x = coin.x - COIN_RADIUS
                        coin.rect.y = coin.y - COIN_RADIUS
                coin.draw(virtual_surface)

            for p in powerups[:]:
                p.update(scroll_speed)
                p.draw(virtual_surface)
                if p.rect.colliderect(player.get_hitbox()):
                    print("Powerup collected!")
                    if p.type == 'invincibility':
                        player.invincible = True
                        speed_multiplier = 3.0  # Triple the overall game speed
                        powerup_text = "Invincibility Activated!"
                    elif p.type == 'magnet':
                        player.magnet = True
                        powerup_text = "Magnet Power Activated!"
                    elif p.type == 'bullet':
                        player.can_shoot = True
                        powerup_text = "Bullet Power Activated!"
                    player.powerup_timer = pygame.time.get_ticks()
                    powerup_text_timer = 60
                    powerups.remove(p)

            player.draw(virtual_surface)

            display_text(f"Coins: {player.coins_collected}", 30, 10, 10)
            display_text(f"Distance: {int(player.distance_travelled)}", 30, 10, 40)
            
            if powerup_text and powerup_text_timer > 0:
                powerup_text_timer -= 1
                text_surface = font.render(powerup_text, True, GREEN)
                virtual_surface.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, HEIGHT - 50))

            render_to_screen()
            pygame.display.flip()

game_loop()