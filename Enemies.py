import time




class Enemy:
    def __init__(self, x: int, y: int, color: str) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.vx = 0
        self.vy = 0

    

    def update(self) -> None:
        