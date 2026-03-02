import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# Game state
score = 0
wave = 1

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,200,255)


# PLAYER 
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2-30, HEIGHT-60, 60, 20)
        self.speed = 6
        self.lives = 3

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top)

    def reset(self):
        self.rect.centerx = WIDTH//2


# BULLETS 
class Bullet:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x-2,y,5,15)
        self.speed = 8

    def update(self):
        self.rect.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen,WHITE,self.rect)


class EnemyBullet:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x-3,y,6,15)
        self.speed = 5

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(screen,RED,self.rect)

# ENEMY
class Enemy:
    def __init__(self,x,y):
        self.base_x = x
        self.base_y = y
        self.rect = pygame.Rect(x,y,35,35)

    def update(self, offset_x, offset_y):
        self.rect.x = self.base_x + offset_x
        self.rect.y = self.base_y + offset_y

    def draw(self):
        pygame.draw.rect(screen,RED,self.rect)


# WALL 
class WallBlock:
    def __init__(self,x,y):
        self.rect = pygame.Rect(x,y,15,15)

    def draw(self):
        pygame.draw.rect(screen,BLUE,self.rect)


# CREATE FUNCTIONS 
def create_walls():
    walls=[]
    base_y = HEIGHT-200
    positions=[200,400,600,800]

    for pos in positions:
        for r in range(4):
            for c in range(6):
                walls.append(WallBlock(pos+c*15,base_y+r*15))
    return walls


def create_enemies(current_wave):
    enemies=[]
    rows = 3 + (current_wave//3)
    cols = 12

    for r in range(rows):
        for c in range(cols):
            x = 80 + c*60
            y = 100 + r*60
            enemies.append(Enemy(x,y))

    return enemies


# INITIAL SETUP 
player = Player()

bullets=[]
enemy_bullets=[]
walls=create_walls()
enemies=create_enemies(wave)

enemy_speed = 2
enemy_direction = 1
offset_x = 0
offset_y = 0

running=True

# GAME LOOP 
while running:

    clock.tick(60)
    screen.fill(BLACK)

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(player.shoot())

    keys=pygame.key.get_pressed()
    player.move(keys)

    # PLAYER BULLETS
    for bullet in bullets[:]:
        bullet.update()
        if bullet.rect.bottom < 0:
            bullets.remove(bullet)

    # ENEMY BULLETS
    for bullet in enemy_bullets[:]:
        bullet.update()
        if bullet.rect.top > HEIGHT:
            enemy_bullets.remove(bullet)

    # ENEMY SHOOTING
    shoot_chance = max(10,40-wave*3)

    if enemies and random.randint(0,shoot_chance)==1:
        shooter=random.choice(enemies)
        enemy_bullets.append(
            EnemyBullet(shooter.rect.centerx, shooter.rect.bottom)
        )

    # ENEMY FORMATION MOVEMENT
    offset_x += enemy_speed * enemy_direction

    move_down=False

    for enemy in enemies:
        if enemy.base_x + offset_x > WIDTH-40 or enemy.base_x + offset_x < 0:
            move_down=True
            break

    if move_down:
        enemy_direction *= -1
        offset_y += 20

    # UPDATE ENEMY POSITIONS
    for enemy in enemies:
        enemy.update(offset_x, offset_y)

    # BULLET HITS ENEMY
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.rect.colliderect(enemy.rect):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score+=100
                break

    # BULLETS HIT WALLS
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

    # ENEMY BULLET HITS PLAYER
    for bullet in enemy_bullets[:]:
        if bullet.rect.colliderect(player.rect):
            enemy_bullets.remove(bullet)
            player.lives -=1
            player.reset()
            pygame.time.delay(500)

    # WAVE CLEAR
    if not enemies:
        wave +=1
        enemy_speed +=0.5
        offset_x=0
        offset_y=0
        enemies=create_enemies(wave)
        walls=create_walls()
        bullets.clear()
        enemy_bullets.clear()
        pygame.time.delay(800)

    # GAME OVER
    if player.lives<=0:
        text=font.render("GAME OVER",True,WHITE)
        screen.blit(text,(WIDTH//2-100,HEIGHT//2))
        pygame.display.flip()
        pygame.time.delay(3000)
        break

    # DRAW
    player.draw()

    for bullet in bullets:
        bullet.draw()

    for bullet in enemy_bullets:
        bullet.draw()

    for enemy in enemies:
        enemy.draw()

    for block in walls:
        block.draw()

    screen.blit(font.render(f"Lives: {player.lives}",True,WHITE),(20,20))
    screen.blit(font.render(f"Score: {score}",True,WHITE),(WIDTH-200,20))
    screen.blit(font.render(f"Wave: {wave}",True,WHITE),(WIDTH//2-60,20))

    pygame.display.flip()

pygame.quit()
sys.exit()