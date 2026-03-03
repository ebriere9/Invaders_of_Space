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
kills = 0
POWERUP_DURATION = 600  # 10 seconds at 60fps

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,200,255)

# PLAYER 
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2-30, HEIGHT-60, 60, 20)
        self.base_speed = 6
        self.speed = self.base_speed
        self.lives = 3

        self.double_shot = False
        self.double_timer = 0

        self.speed_boost = False
        self.speed_timer = 0

        self.shield = False

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

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)
        if self.shield:
            pygame.draw.rect(screen, (0,150,255), self.rect.inflate(10,10), 3)

    def shoot(self):
        if self.double_shot:
            return [
                Bullet(self.rect.left + 10, self.rect.top),
                Bullet(self.rect.right - 10, self.rect.top)
            ]
        return [Bullet(self.rect.centerx, self.rect.top)]

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


# POWERUP
class PowerUp:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.speed = 3
        self.type = type

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        colors = {
            "double": (255,215,0),
            "speed": (0,255,255),
            "shield": (0,150,255),
            "life": (255,0,255)
        }
        pygame.draw.rect(screen, colors[self.type], self.rect)


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
powerups=[]
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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.extend(player.shoot())

    keys=pygame.key.get_pressed()
    player.move(keys)
    player.update_powerups()

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

    # ENEMY MOVEMENT
    offset_x += enemy_speed * enemy_direction
    move_down=False

    for enemy in enemies:
        if enemy.base_x + offset_x > WIDTH-40 or enemy.base_x + offset_x < 0:
            move_down=True
            break

    if move_down:
        enemy_direction *= -1
        offset_y += 20

    for enemy in enemies:
        enemy.update(offset_x, offset_y)

    # BULLET HITS ENEMY
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.rect.colliderect(enemy.rect):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score+=100
                kills+=1

                if kills % 10 == 0:
                    power_type=random.choice(["double","speed","shield","life"])
                    powerups.append(PowerUp(enemy.rect.centerx, enemy.rect.centery, power_type))
                break

    # POWERUP UPDATE
    for power in powerups[:]:
        power.update()
        if power.rect.top > HEIGHT:
            powerups.remove(power)

        if power.rect.colliderect(player.rect):
            if power.type=="double":
                player.double_shot=True
                player.double_timer=POWERUP_DURATION
            elif power.type=="speed":
                player.speed_boost=True
                player.speed_timer=POWERUP_DURATION
                player.speed=player.base_speed+4
            elif power.type=="shield":
                player.shield=True
            elif power.type=="life":
                player.lives+=1
            powerups.remove(power)

    # ENEMY BULLET HITS PLAYER
    for bullet in enemy_bullets[:]:
        if bullet.rect.colliderect(player.rect):
            enemy_bullets.remove(bullet)
            if player.shield:
                player.shield=False
            else:
                player.lives-=1
            player.reset()
            pygame.time.delay(300)

    # WAVE CLEAR
    if not enemies:
        wave+=1
        enemy_speed+=0.5
        offset_x=0
        offset_y=0
        enemies=create_enemies(wave)
        walls=create_walls()
        bullets.clear()
        enemy_bullets.clear()
        pygame.time.delay(800)

    # GAME OVER
    if player.lives<=0:
        text = font.render("GAME OVER",True,WHITE)
        screen.blit(text,(WIDTH//2-100,HEIGHT//2))
        text2 = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text2, (WIDTH//2-100, HEIGHT//2+50))

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

    for power in powerups:
        power.draw()

    # UI
    screen.blit(font.render(f"Lives: {player.lives}",True,WHITE),(20,20))
    screen.blit(font.render(f"Score: {score}",True,WHITE),(WIDTH-200,20))
    screen.blit(font.render(f"Wave: {wave}",True,WHITE),(WIDTH//2-60,20))

    if player.double_shot:
        screen.blit(font.render("DOUBLE SHOT",True,(255,215,0)),(20,60))
    if player.speed_boost:
        screen.blit(font.render("SPEED BOOST",True,(0,255,255)),(20,100))
    if player.shield:
        screen.blit(font.render("SHIELD",True,(0,150,255)),(20,140))

    pygame.display.flip()

pygame.quit()
sys.exit()