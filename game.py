import pygame
from settings import *


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("贪吃蛇 - Snake")
        self.clock = pygame.time.Clock()
        self.running = True
        self.init_game()

    def init_game(self):
        cx, cy = COLS // 2, ROWS // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

    def set_direction(self, dx, dy):
        if (dx, dy) == (-self.direction[0], -self.direction[1]):
            return
        self.next_direction = (dx, dy)

    def step(self):
        self.direction = self.next_direction
        head = self.snake[0]
        new_head = (head[0] + self.direction[0],
                    head[1] + self.direction[1])

        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            self.running = False
            return

        if new_head in self.snake:
            self.running = False
            return

        self.snake.insert(0, new_head)
        self.snake.pop()

    def draw(self):
        self.screen.fill(BG_COLOR)
        for x in range(COLS):
            for y in range(ROWS):
                rect = pygame.Rect(
                    x * CELL_SIZE, y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

        for sx, sy in self.snake:
            x = sx * CELL_SIZE + 1
            y = sy * CELL_SIZE + 1
            w = CELL_SIZE - 2
            pygame.draw.rect(self.screen, (80, 220, 120),
                             (x, y, w, w), border_radius=4)

        pygame.display.flip()

    def run(self):
        while self.running:
            self._handle_events()
            self.step()
            self.draw()
            self.clock.tick(1000 // BASE_SPEED)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.set_direction(0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.set_direction(0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.set_direction(-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.set_direction(1, 0)
