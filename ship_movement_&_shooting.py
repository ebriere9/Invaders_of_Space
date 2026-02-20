import pygame
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Movement & Shooting")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

clock = pygame.time.Clock()


# =========================
# Player (Ship) Class
# =========================
class Player:
    def __init__(self):
        self.width = 60
        self.height = 20
        self.rect = pygame.Rect(
            WIDTH // 2 - self.width // 2,
            HEIGHT - 60,
            self.width,
            self.height
        )
        self.speed = 6

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.rect)

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top)


# =========================
# Bullet Class
# =========================
class Bullet:
    def __init__(self, x, y):
        self.width = 5
        self.height = 15
        self.speed = 8
        self.rect = pygame.Rect(
            x - self.width // 2,
            y,
            self.width,
            self.height
        )

    def move(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

    def off_screen(self):
        return self.rect.bottom < 0


# =========================
# Game Setup
# =========================
player = Player()
bullets = []

running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(player.shoot())

    # Movement
    keys = pygame.key.get_pressed()
    player.move(keys)

    # Update bullets
    for bullet in bullets[:]:
        bullet.move()
        if bullet.off_screen():
            bullets.remove(bullet)

    # Draw everything
    player.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()