import sys
import time

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
    





def main():
    fps = 60
    fps_clock = pygame.time.Clock()



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


    while True:
        screen.fill("#000000")
            

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()

        for enemy in enemies:
            enemy.display()
        for enemy in enemies:
            enemy.update()

   

    




        pygame.display.flip()
        fps_clock.tick(fps)


if __name__ == "__main__":
    main()