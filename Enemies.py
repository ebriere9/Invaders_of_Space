import sys
import time
import random

import pygame
import pygame.locals


WIDTH, HEIGHT = 1000, 1000
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))




class Enemy:
    def __init__(self, x: int, y: int, surface: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.color = "#0DFF00"
        self.vx = 0
        self.vy = 0
        self.surface = surface


    

    def update(self) -> None:
        self.y += 0.25



    def display(self) -> None:
        pygame.draw.rect(screen, self.color, (self.x, self.y, 35, 35))

    def shoot(self):
        if random.random() < 0.1:
            return Bullet2(10, screen)
        else:
            return None

    
class Bullet2:
    def __init__(self, x: int, surface: pygame.Surface) -> None:
        self.surface = surface
        self.vy = 5
        self.x = x

    def updateB(self):
        self.y += self.vy

    def displayB(self):
        pygame.draw.rect(screen, "#FF0000", (self.x, self.y, 5, 10))



def main():
    fps = 60
    fps_clock = pygame.time.Clock()





    # Enemies in a row
    enemies = []
    start_x = 35
    start_y = 100
    spacing = 75
    num_enemies = 39

    for j in range(num_enemies):
        if j <= 12:
            for i in range(num_enemies):
                x = start_x + i * spacing # The new x value of the enemy is spacing times the enemies number in the row added to the start
                enemy = Enemy(x, start_y, screen)
                enemies.append(enemy) 
        elif j > 12 and j <= 25:
            for i in range(num_enemies):
                start_y = 175
                x = start_x + i * spacing
                enemy = Enemy(x, start_y, screen)
                enemies.append(enemy)
        elif j > 25 and j <= 38:
            for i in range(num_enemies):
                start_y = 250
                x = start_x + i * spacing
                enemy = Enemy(x, start_y, screen)
                enemies.append(enemy)


    # Bullet
    Bullets = []
   


    while True:
        screen.fill("#000000")
            

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()
        for enemy in enemies:
            chance = enemy.shoot()
            if chance != None:
                Bullets.append(chance)

        for enemy in enemies:
            enemy.update()
        for enemy in enemies:
            enemy.display()



        for bullet in Bullets:
            bullet.updateB()
        for bullet in Bullets:
            bullet.displayB()
    




        pygame.display.flip()
        fps_clock.tick(fps)


if __name__ == "__main__":
    main()