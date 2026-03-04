import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Final Version")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
BLUE = (0, 200, 255)
YELLOW = (255, 215, 0)
SHIELD_BLUE = (0, 150, 255)
MAGNETA = (255, 0 ,255)

score = 0
wave = 1
MAX_LIVES = 3
POWERUP_DURATION = 600
kills = 0

# Player
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - 30, HEIGHT - 60, 60, 20)
        self.base_speed = 6
        self.speed = self.base_speed
        self.lives = MAX_LIVES

        # Powerup variables
        self.double_shot = False
        self.double_timer = 0

        self.speed_boost = False
        self.speed_timer = 0

        self.shield = False
        self.shield_timer = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def update_powerups(self):
        if self.double_shot:
            self.double_timer -= 1
            if self.double_timer <= 0:
                self.double_shot = False

        if self.speed_boost:
            self.speed_timer -= 1
            if self.speed_timer <= 0:
                self.speed_boost = False
                self.speed = self.base_speed

        if self.shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)
        if self.shield:
            pygame.draw.rect(screen, SHIELD_BLUE, self.rect.inflate(10,10), 3)

    def shoot(self):
        if self.double_shot:
            return [
                Bullet(self.rect.left + 10, self.rect.top),
                Bullet(self.rect.right - 10, self.rect.top)
            ]
        return [Bullet(self.rect.centerx, self.rect.top)]

    def reset(self):
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10


# Bullet
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 2, y, 5, 15)
        self.speed = 8

    def update(self):
        self.rect.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)


# Enemy bullet
class EnemyBullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 3, y, 6, 15)
        self.speed = 5

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)


# Enemy
class Enemy:
    def __init__(self, x, y):
        self.base_x = x
        self.base_y = y
        self.rect = pygame.Rect(x, y, 35, 35)

    def update(self, offset_x, offset_y):
        self.rect.x = self.base_x + offset_x
        self.rect.y = self.base_y + offset_y

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)


# Walls 
class WallBlock:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 15, 15)

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)


# Powerups
class PowerUp:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.speed = 3
        self.type = type

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        colors = {
            "double": YELLOW,
            "speed": CYAN,
            "shield": SHIELD_BLUE,
            "life": MAGNETA,
        }
        pygame.draw.rect(screen, colors[self.type], self.rect)


def create_walls():
    walls = []
    base_y = HEIGHT - 200
    positions = [200, 400, 600, 800]

    for pos in positions:
        for r in range(4):
            for c in range(6):
                walls.append(WallBlock(pos + c*15, base_y + r*15))

    return walls


def create_enemies(current_wave):
    enemies = []
    rows = 3 + (current_wave // 3)
    cols = 12

    for r in range(rows):
        for c in range(cols):
            x = 80 + c * 60
            y = 100 + r * 60
            enemies.append(Enemy(x, y))

    return enemies


player = Player()
bullets = []
powerups = []
enemy_bullets = []
walls = create_walls()
enemies = create_enemies(wave)

enemy_speed = 2
enemy_direction = 1
offset_x = 0
offset_y = 0

running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.extend(player.shoot())

    keys = pygame.key.get_pressed()
    player.move(keys)
    player.update_powerups()

    # Player bullets
    for bullet in bullets[:]:
        bullet.update()
        if bullet.rect.bottom < 0:
            bullets.remove(bullet)

    # Enemy bullets
    for bullet in enemy_bullets[:]:
        bullet.update()
        if bullet.rect.top > HEIGHT:
            enemy_bullets.remove(bullet)

    # Enemy shooting
    if enemies and random.randint(0, max(10, 40 - wave*3)) == 1:
        shooter = random.choice(enemies)
        enemy_bullets.append(
            EnemyBullet(shooter.rect.centerx, shooter.rect.bottom)
        )

    # Enemy Movement
    offset_x += enemy_speed * enemy_direction
    move_down = False

    for enemy in enemies:
        if enemy.base_x + offset_x > WIDTH - 40 or enemy.base_x + offset_x < 0:
            move_down = True
            break

    if move_down:
        enemy_direction *= -1
        offset_y += 20

    for enemy in enemies:
        enemy.update(offset_x, offset_y)

    # Player bullets hit enemy
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.rect.colliderect(enemy.rect):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 100
                kills += 1
                if kills % 20 == 0:
                    power_type = random.choice(["double", "speed","shield", "life"])
                    powerups.append(PowerUp(enemy.rect.centerx, enemy.rect.centery, power_type))
                break

    # Powerups update
    for powerup in powerups[:]:
        powerup.update()
        powerup.draw()
        if powerup.rect.colliderect(player.rect):
            if powerup.type == "double":
                player.double_shot = True
                player.double_timer = POWERUP_DURATION
            elif powerup.type == "speed":
                player.speed_boost = True
                player.speed = 10
                player.speed_timer = POWERUP_DURATION
            elif powerup.type == "shield":
                player.shield = True
                player.shield_timer = POWERUP_DURATION
            elif powerup.type == "life":
                if player.lives < MAX_LIVES:
                    player.lives += 1
            powerups.remove(powerup)

    # Enemy bullets hit player
    for bullet in enemy_bullets[:]:
        if bullet.rect.colliderect(player.rect):
            enemy_bullets.remove(bullet)
            if player.shield:
                player.shield = False
                player.shield_timer = 0
            else:
                player.lives -= 1
                player.reset()
                pygame.time.delay(300)

    # Bullets hit walls
    for bullet in bullets[:]:
        for block in walls[:]:
            if bullet.rect.colliderect(block.rect):
                bullets.remove(bullet)
                walls.remove(block)
                break

    for bullet in enemy_bullets[:]:
        for block in walls[:]:
            if bullet.rect.colliderect(block.rect):
                enemy_bullets.remove(bullet)
                walls.remove(block)
                break

    # Wave clear
    if not enemies:
        wave += 1
        enemy_speed += 0.5
        offset_x = 0
        offset_y = 0
        enemies = create_enemies(wave)
        walls = create_walls()
        bullets.clear()
        enemy_bullets.clear()
        pygame.time.delay(800)


    if player.lives <= 0:
        game_over_text = font.render("GAME OVER", True, WHITE)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - 120, HEIGHT//2))
        screen.blit(score_text, (WIDTH//2 - 120, HEIGHT//2 + 50))
        pygame.display.flip()
        pygame.time.delay(3000)
        break

    
    player.draw()
    for bullet in bullets:
        bullet.draw()
    for bullet in enemy_bullets:
        bullet.draw()
    for enemy in enemies:
        enemy.draw()
    for block in walls:
        block.draw()
    for power in powerups:
        power.draw()


    screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (20, 20))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (WIDTH - 200, 20))
    screen.blit(font.render(f"Wave: {wave}", True, WHITE), (WIDTH//2 - 60, 20))
    if player.double_shot:
        screen.blit(font.render("DOUBLE SHOT", True, YELLOW), (20, 60))
    if player.speed_boost:
        screen.blit(font.render("SPEED BOOST", True, CYAN), (20, 100))
    if player.shield:
        screen.blit(font.render("SHIELD", True, SHIELD_BLUE), (20, 140))

    pygame.display.flip()

pygame.quit()
sys.exit()