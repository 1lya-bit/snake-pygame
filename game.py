import random
import json
import pygame
from settings import *


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("贪吃蛇 - Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("microsoftyahei", 20)
        self.font_small = pygame.font.SysFont("microsoftyahei", 14)
        self.running = True
        self.paused = False
        self.game_over_flag = False
        self.init_game()

    def init_game(self):
        cx, cy = COLS // 2, ROWS // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self._place_food()
        self.score = 0
        self.speed = BASE_SPEED
        self.high_score = self._load_high_score()
        self.game_over_flag = False
        self.paused = False

    def _place_food(self):
        occupied = set(self.snake)
        free = [(x, y) for x in range(COLS) for y in range(ROWS)
                if (x, y) not in occupied]
        return random.choice(free) if free else None

    def _load_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return json.load(f).get("high_score", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def _save_high_score(self):
        with open(HIGH_SCORE_FILE, "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def set_direction(self, dx, dy):
        if (dx, dy) == (-self.direction[0], -self.direction[1]):
            return
        self.next_direction = (dx, dy)

    def toggle_pause(self):
        if self.game_over_flag:
            return
        self.paused = not self.paused

    def step(self):
        if self.game_over_flag or self.paused:
            return

        self.direction = self.next_direction
        head = self.snake[0]
        new_head = (head[0] + self.direction[0],
                    head[1] + self.direction[1])

        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            self._game_over()
            return

        if new_head in self.snake:
            self._game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += POINTS_PER_FOOD
            self.speed = max(MIN_SPEED, self.speed - SPEED_INCREMENT)
            self.food = self._place_food()
            if self.food is None:
                self._win()
                return
        else:
            self.snake.pop()

    def _game_over(self):
        self.game_over_flag = True
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    def _win(self):
        self.game_over_flag = True
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    def draw(self):
        self.screen.fill(BG_COLOR)

        for x in range(COLS):
            for y in range(ROWS):
                rect = pygame.Rect(
                    x * CELL_SIZE, y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, GRID_COLOR, rect, GRID_WIDTH)

        if self.food:
            fx, fy = self.food
            cx = fx * CELL_SIZE + CELL_SIZE // 2
            cy = fy * CELL_SIZE + CELL_SIZE // 2
            r = CELL_SIZE // 2 - 2
            for i in range(3, 0, -1):
                alpha = 60 // i
                color = (255, 80 + i * 20, 80 + i * 20)
                pygame.draw.circle(self.screen, color, (cx, cy), r + i * 2)
            pygame.draw.circle(self.screen, FOOD_COLOR, (cx, cy), r)

        for i, (sx, sy) in enumerate(self.snake):
            x = sx * CELL_SIZE + 1
            y = sy * CELL_SIZE + 1
            w = CELL_SIZE - 2

            if i == 0:
                color = SNAKE_HEAD_COLOR
            else:
                t = i / max(len(self.snake) - 1, 1)
                r_val = int(SNAKE_BODY_START[0] + t * (SNAKE_BODY_END[0] - SNAKE_BODY_START[0]))
                g_val = int(SNAKE_BODY_START[1] + t * (SNAKE_BODY_END[1] - SNAKE_BODY_START[1]))
                b_val = int(SNAKE_BODY_START[2] + t * (SNAKE_BODY_END[2] - SNAKE_BODY_START[2]))
                color = (r_val, g_val, b_val)

            radius = 6 if i == 0 else 4
            pygame.draw.rect(self.screen, color, (x, y, w, w), border_radius=radius)

            if i == 0:
                eye_size = 3
                eye_color = (255, 255, 255)
                mid_x, mid_y = x + w // 2, y + w // 2
                dx, dy = self.direction
                if dx == 1:
                    pygame.draw.rect(self.screen, eye_color, (mid_x + 3, mid_y - 5, eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, (mid_x + 3, mid_y + 2, eye_size, eye_size))
                elif dx == -1:
                    pygame.draw.rect(self.screen, eye_color, (mid_x - 6, mid_y - 5, eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, (mid_x - 6, mid_y + 2, eye_size, eye_size))
                elif dy == -1:
                    pygame.draw.rect(self.screen, eye_color, (mid_x - 5, mid_y - 6, eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, (mid_x + 2, mid_y - 6, eye_size, eye_size))
                elif dy == 1:
                    pygame.draw.rect(self.screen, eye_color, (mid_x - 5, mid_y + 3, eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, (mid_x + 2, mid_y + 3, eye_size, eye_size))

        bar_y = ROWS * CELL_SIZE
        pygame.draw.rect(self.screen, (10, 10, 25),
                         (0, bar_y, WINDOW_W, WINDOW_H - bar_y))
        score_text = self.font.render(f"分数: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (12, bar_y + 10))
        high_text = self.font_small.render(f"最高分: {self.high_score}", True, ACCENT_COLOR)
        self.screen.blit(high_text, (12, bar_y + 34))
        speed_text = self.font_small.render(f"速度: {BASE_SPEED - self.speed + MIN_SPEED}", True, (150, 150, 150))
        speed_rect = speed_text.get_rect(right=WINDOW_W - 12, centery=bar_y + 22)
        self.screen.blit(speed_text, speed_rect)

        if self.game_over_flag:
            overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))
            go_font = pygame.font.SysFont("microsoftyahei", 48, bold=True)
            if self.food is None and len(self.snake) == COLS * ROWS:
                msg = "你赢了!"
                msg_color = (0, 255, 100)
            else:
                msg = "游戏结束"
                msg_color = (255, 107, 107)
            go_text = go_font.render(msg, True, msg_color)
            go_rect = go_text.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 - 30))
            self.screen.blit(go_text, go_rect)
            restart_text = self.font.render("按 R 重新开始 | 按 Q 退出", True, TEXT_COLOR)
            restart_rect = restart_text.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 25))
            self.screen.blit(restart_text, restart_rect)

        elif self.paused:
            overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))
            pause_font = pygame.font.SysFont("microsoftyahei", 36, bold=True)
            pause_text = pause_font.render("已暂停", True, TEXT_COLOR)
            pause_rect = pause_text.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 - 20))
            self.screen.blit(pause_text, pause_rect)
            tip_text = self.font_small.render("按 空格 继续", True, (180, 180, 180))
            tip_rect = tip_text.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 20))
            self.screen.blit(tip_text, tip_rect)

        elif not self.game_over_flag and self.snake == [(COLS // 2, ROWS // 2), (COLS // 2 - 1, ROWS // 2), (COLS // 2 - 2, ROWS // 2)]:
            tip = self.font_small.render("按 方向键/WASD 开始", True, (120, 120, 120))
            tip_rect = tip.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 60))
            self.screen.blit(tip, tip_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self._handle_events()
            if not self.paused and not self.game_over_flag:
                self.step()
            self.draw()
            self.clock.tick(1000 // self.speed)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_over_flag:
                    if event.key == pygame.K_r:
                        self.init_game()
                    elif event.key == pygame.K_q:
                        self.running = False
                elif event.key == pygame.K_SPACE:
                    self.toggle_pause()
                elif not self.paused:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.set_direction(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.set_direction(0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.set_direction(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.set_direction(1, 0)
