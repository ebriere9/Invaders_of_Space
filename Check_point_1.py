import pygame
import sys

# Initialize
pygame.init()

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


# Player Class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 30, HEIGHT - 60, 60, 20)
        self.speed = 6
        self.lives = 3  

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.rect)

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top)

    def reset_position(self):
        self.rect.centerx = WIDTH // 2



# Bullet Class
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 2, y, 5, 15)
        self.speed = 8

    def move(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

    def off_screen(self):
        return self.rect.bottom < 0



# Enemy Class
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 35, 35)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)



# Create Enemy Grid
def create_enemies():
    enemies = []
    rows = 3
    cols = 12
    start_x = 50
    start_y = 100
    spacing_x = 70
    spacing_y = 70

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            enemies.append(Enemy(x, y))
    return enemies


enemies = create_enemies()

# Enemy movement variables
enemy_direction = 1
enemy_speed = 2
move_down_amount = 20

player = Player()
bullets = []

running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(player.shoot())

    # Player movement
    keys = pygame.key.get_pressed()
    player.move(keys)

    # Update bullets
    for bullet in bullets[:]:
        bullet.move()
        if bullet.off_screen():
            bullets.remove(bullet)

    # Enemy movement
    move_down = False
    for enemy in enemies:
        enemy.rect.x += enemy_speed * enemy_direction
        if enemy.rect.right >= WIDTH or enemy.rect.left <= 0:
            move_down = True

    if move_down:
        enemy_direction *= -1
        for enemy in enemies:
            enemy.rect.y += move_down_amount

    # Bullet collision
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.rect.colliderect(enemy.rect):
                bullets.remove(bullet)
                enemies.remove(enemy)
                break

    # Player hit by enemy
    for enemy in enemies:
        if enemy.rect.colliderect(player.rect):
            player.lives -= 1
            player.reset_position()
            enemies = create_enemies()
            bullets.clear()
            pygame.time.delay(500)
            break

    # Game Over
    if player.lives <= 0:
        game_over_text = font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

    # Draw everything
    player.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

    

    for enemy in enemies:
        enemy.draw(screen)

    # Draw lives
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    screen.blit(lives_text, (20, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()