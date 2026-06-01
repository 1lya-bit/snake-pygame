import pygame
from settings import *


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("贪吃蛇 - Snake")
        self.clock = pygame.time.Clock()
        self.running = True

    def draw(self):
        """绘制网格背景"""
        self.screen.fill(BG_COLOR)
        for x in range(COLS):
            for y in range(ROWS):
                rect = pygame.Rect(
                    x * CELL_SIZE, y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)
        pygame.display.flip()

    def run(self):
        """主循环"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.draw()
            self.clock.tick(60)
