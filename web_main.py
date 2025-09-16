#!/usr/bin/env python3
"""
Web-optimized version of RoboRun for Pygbag deployment.
This version includes responsive scaling and web-specific optimizations.
"""

import pygame
import random
import sys
import math
import os
from PIL import Image, ImageSequence

# Use the current working directory for asset loading
ASSET_DIR = os.getcwd()

pygame.init()

# Base virtual resolution - optimized for web
BASE_WIDTH, BASE_HEIGHT = 1024, 768
FPS = 60

# For web deployment, we'll use responsive scaling
# Get screen resolution (will be browser window size)
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h

# Calculate scaling factors for responsive design
SCALE_X = SCREEN_WIDTH / BASE_WIDTH
SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT
SCALE = min(SCALE_X, SCALE_Y)  # Maintain aspect ratio

# Calculate actual window size
WINDOW_WIDTH = int(BASE_WIDTH * SCALE)
WINDOW_HEIGHT = int(BASE_HEIGHT * SCALE)

# Calculate centering offsets
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

# Create the display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
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
    # Clear the screen
    screen.fill(BLACK)
    
    # Scale the virtual surface to fill the screen while maintaining aspect ratio
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

# Load fonts with scaling
try:
    font = pygame.font.Font(None, int(36 * SCALE))
    small_font = pygame.font.Font(None, int(24 * SCALE))
except:
    font = pygame.font.SysFont(None, int(36 * SCALE))
    small_font = pygame.font.SysFont(None, int(24 * SCALE))

# Load assets with scaling
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

# Import all the game classes and functions from the main file
# This is a simplified version for web deployment
# The full implementation would include all the classes from main.py

def start_screen():
    """Display the start screen with title, controls, and instructions"""
    while True:
        virtual_surface.fill(BLACK)
        
        # Title
        title_font = pygame.font.Font(None, int(72 * SCALE))
        title_text = title_font.render("RoboRun", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        virtual_surface.blit(title_text, title_rect)
        
        # Controls
        controls_text = [
            "Controls:",
            "Arrow Keys or WASD - Move",
            "SPACE - Shoot (when powerup active)",
            "ESC - Pause"
        ]
        
        y_offset = HEIGHT//2 - 60
        for i, text in enumerate(controls_text):
            color = YELLOW if i == 0 else WHITE
            font_size = int(36 * SCALE) if i == 0 else int(28 * SCALE)
            text_surface = pygame.font.Font(None, font_size).render(text, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH//2, y_offset + i * 35))
            virtual_surface.blit(text_surface, text_rect)
        
        # Instructions
        instruction_font = pygame.font.Font(None, int(48 * SCALE))
        instruction_text = instruction_font.render("Press R to Play", True, GREEN)
        instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 100))
        virtual_surface.blit(instruction_text, instruction_rect)
        
        # High score
        if high_score > 0:
            high_score_text = pygame.font.Font(None, int(32 * SCALE)).render(f"High Score: {high_score}", True, GREY)
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

def main():
    """Main function for web deployment"""
    # Show start screen
    start_screen()
    
    # For now, just show a placeholder
    # In a full implementation, this would run the complete game
    print("Game would start here in full implementation")

if __name__ == "__main__":
    main()
