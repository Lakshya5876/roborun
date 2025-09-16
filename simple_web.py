import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game state
class GameState:
    START = "start"
    PLAYING = "playing"
    GAME_OVER = "game_over"

def main():
    # Set up display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("RoboRun - Web Version")
    clock = pygame.time.Clock()
    
    # Fonts
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    
    # Game variables
    game_state = GameState.START
    player_x = WIDTH // 2
    player_y = HEIGHT - 100
    player_size = 40
    score = 0
    bullets = []
    enemies = []
    coins = []
    
    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if game_state == GameState.START:
                        game_state = GameState.PLAYING
                    elif game_state == GameState.GAME_OVER:
                        game_state = GameState.PLAYING
                        score = 0
                        bullets = []
                        enemies = []
                        coins = []
                        player_x = WIDTH // 2
                        player_y = HEIGHT - 100
                elif event.key == pygame.K_SPACE and game_state == GameState.PLAYING:
                    bullets.append([player_x + player_size//2, player_y])
        
        # Handle input
        if game_state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x -= 5
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x += 5
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_y -= 5
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player_y += 5
            
            # Keep player on screen
            player_x = max(0, min(player_x, WIDTH - player_size))
            player_y = max(0, min(player_y, HEIGHT - player_size))
            
            # Update bullets
            for bullet in bullets[:]:
                bullet[1] -= 8
                if bullet[1] < 0:
                    bullets.remove(bullet)
            
            # Update enemies
            for enemy in enemies[:]:
                enemy[1] += 3
                if enemy[1] > HEIGHT:
                    enemies.remove(enemy)
            
            # Update coins
            for coin in coins[:]:
                coin[1] += 2
                if coin[1] > HEIGHT:
                    coins.remove(coin)
            
            # Spawn enemies
            if random.randint(1, 60) == 1:
                enemies.append([random.randint(0, WIDTH - 30), -30])
            
            # Spawn coins
            if random.randint(1, 120) == 1:
                coins.append([random.randint(50, WIDTH - 50), -30])
            
            # Collision detection
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    if (abs(bullet[0] - enemy[0]) < 20 and 
                        abs(bullet[1] - enemy[1]) < 20):
                        bullets.remove(bullet)
                        enemies.remove(enemy)
                        score += 10
            
            # Player collision with enemies
            for enemy in enemies:
                if (abs(player_x - enemy[0]) < 30 and 
                    abs(player_y - enemy[1]) < 30):
                    game_state = GameState.GAME_OVER
            
            # Player collision with coins
            for coin in coins[:]:
                if (abs(player_x - coin[0]) < 30 and 
                    abs(player_y - coin[1]) < 30):
                    coins.remove(coin)
                    score += 5
        
        # Draw everything
        screen.fill(BLACK)
        
        if game_state == GameState.START:
            # Start screen
            title = font_large.render("RoboRun", True, GREEN)
            title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            screen.blit(title, title_rect)
            
            controls = [
                "Arrow Keys or WASD - Move",
                "Space - Shoot",
                "R - Start/Restart"
            ]
            
            for i, control in enumerate(controls):
                text = font_small.render(control, True, WHITE)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20 + i * 30))
                screen.blit(text, text_rect)
            
            start_text = font_medium.render("Press R to Start!", True, YELLOW)
            start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
            screen.blit(start_text, start_rect)
            
        elif game_state == GameState.PLAYING:
            # Draw player
            pygame.draw.rect(screen, GREEN, (player_x, player_y, player_size, player_size))
            pygame.draw.rect(screen, WHITE, (player_x, player_y, player_size, player_size), 2)
            
            # Draw bullets
            for bullet in bullets:
                pygame.draw.circle(screen, YELLOW, (int(bullet[0]), int(bullet[1])), 5)
            
            # Draw enemies
            for enemy in enemies:
                pygame.draw.rect(screen, RED, (enemy[0], enemy[1], 30, 30))
                pygame.draw.rect(screen, WHITE, (enemy[0], enemy[1], 30, 30), 2)
            
            # Draw coins
            for coin in coins:
                pygame.draw.circle(screen, YELLOW, (int(coin[0]), int(coin[1])), 15)
                pygame.draw.circle(screen, WHITE, (int(coin[0]), int(coin[1])), 15, 2)
            
            # Draw score
            score_text = font_small.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
        elif game_state == GameState.GAME_OVER:
            # Game over screen
            game_over = font_large.render("Game Over!", True, RED)
            game_over_rect = game_over.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(game_over, game_over_rect)
            
            score_text = font_medium.render(f"Score: {score}", True, WHITE)
            score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(score_text, score_rect)
            
            restart_text = font_medium.render("Press R to Restart", True, YELLOW)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
