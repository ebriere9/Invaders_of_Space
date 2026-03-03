import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,200,255)

POWERUP_DURATION = 600


# PLAYER 
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2-30, HEIGHT-60, 60, 20)
        self.base_speed = 6
        self.speed = self.base_speed
        
        self.max_lives = 3
        self.lives = self.max_lives

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

    def add_life(self):
        if self.lives < self.max_lives:
            self.lives += 1

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


def reset_game():
    return {
        "score":0,
        "wave":1,
        "kills":0,
        "enemy_speed":2,
        "enemy_direction":1,
        "offset_x":0,
        "offset_y":0,
        "player":Player(),
        "bullets":[],
        "enemy_bullets":[],
        "powerups":[],
        "walls":create_walls(),
        "enemies":create_enemies(1)
    }


# INITIAL GAME STATE
game = reset_game()

running = True

# MAIN LOOP
while running:

    clock.tick(60)
    screen.fill(BLACK)

    player = game["player"]
    bullets = game["bullets"]
    enemy_bullets = game["enemy_bullets"]
    powerups = game["powerups"]
    walls = game["walls"]
    enemies = game["enemies"]

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.extend(player.shoot())

    keys=pygame.key.get_pressed()
    player.move(keys)
    player.update_powerups()

    # UPDATE BULLETS
    for bullet in bullets[:]:
        bullet.update()
        if bullet.rect.bottom < 0:
            bullets.remove(bullet)

    for bullet in enemy_bullets[:]:
        bullet.update()
        if bullet.rect.top > HEIGHT:
            enemy_bullets.remove(bullet)

    # ENEMY SHOOTING
    shoot_chance = max(10,40-game["wave"]*3)
    if enemies and random.randint(0,shoot_chance)==1:
        shooter=random.choice(enemies)
        enemy_bullets.append(
            EnemyBullet(shooter.rect.centerx, shooter.rect.bottom)
        )

    # ENEMY MOVEMENT
    game["offset_x"] += game["enemy_speed"] * game["enemy_direction"]
    move_down=False

    for enemy in enemies:
        if enemy.base_x + game["offset_x"] > WIDTH-40 or enemy.base_x + game["offset_x"] < 0:
            move_down=True
            break

    if move_down:
        game["enemy_direction"] *= -1
        game["offset_y"] += 20

    for enemy in enemies:
        enemy.update(game["offset_x"], game["offset_y"])

    # BULLET HITS ENEMY
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.rect.colliderect(enemy.rect):
                bullets.remove(bullet)
                enemies.remove(enemy)
                game["score"]+=100
                game["kills"]+=1

                if game["kills"] % 10 == 0:
                    power_choices=["double","speed","shield"]
                    if player.lives < player.max_lives:
                        power_choices.append("life")
                    powerups.append(
                        PowerUp(enemy.rect.centerx, enemy.rect.centery, random.choice(power_choices))
                    )
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

    # POWERUPS
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
                player.add_life()
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

    # WAVE CLEAR
    if not enemies:
        game["wave"]+=1
        game["enemy_speed"]+=0.5
        game["offset_x"]=0
        game["offset_y"]=0
        game["walls"]=create_walls()
        game["enemies"]=create_enemies(game["wave"])

    # GAME OVER SCREEN
    if player.lives <= 0:
        while True:
            screen.fill(BLACK)

            game_over_text = font.render("GAME OVER", True, WHITE)
            score_text = font.render(f"Final Score: {game['score']}", True, WHITE)
            restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)

            screen.blit(game_over_text, (WIDTH//2 - 120, HEIGHT//2 - 60))
            screen.blit(score_text, (WIDTH//2 - 140, HEIGHT//2))
            screen.blit(restart_text, (WIDTH//2 - 220, HEIGHT//2 + 60))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        game = reset_game()
                        break
            else:
                continue
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

    screen.blit(font.render(f"Lives: {player.lives}",True,WHITE),(20,20))
    screen.blit(font.render(f"Score: {game['score']}",True,WHITE),(WIDTH-200,20))
    screen.blit(font.render(f"Wave: {game['wave']}",True,WHITE),(WIDTH//2-60,20))

    pygame.display.flip()

pygame.quit()
sys.exit() 

