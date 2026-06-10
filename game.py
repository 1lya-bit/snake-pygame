"""贪吃蛇游戏主模块。

定义 SnakeGame 类，作为游戏控制器，管理游戏循环、事件处理、
渲染调度及高分持久化。
"""

import json
import pygame
from settings import *
from snake import Snake
from food import Food


class SnakeGame:
    """贪吃蛇游戏主控制器。

    负责初始化 pygame 窗口、管理游戏主循环、处理用户输入、
    协调 Snake 与 Food 对象，并维护计分与最高分持久化。

    属性:
        running: 主循环是否运行中。
        paused: 是否处于暂停状态。
        game_over_flag: 是否处于游戏结束/胜利状态。
        snake: Snake 实例。
        food: Food 实例。
        score: 当前得分。
        speed: 当前游戏速度（数值越小越快）。
        high_score: 历史最高分（从 JSON 文件加载）。
    """

    def __init__(self):
        """初始化 pygame、窗口、字体，创建蛇和食物对象并启动游戏。"""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("贪吃蛇 - Snake")
        self.clock = pygame.time.Clock()

        # 字体：主字体用于分数，小字体用于辅助信息
        self.font = pygame.font.SysFont("microsoftyahei", 20)
        self.font_small = pygame.font.SysFont("microsoftyahei", 14)

        self.running = True
        self.paused = False
        self.game_over_flag = False

        # 核心实体
        self.snake = Snake()
        self.food = Food()

        self.score = 0
        self.speed = BASE_SPEED
        self.high_score = self._load_high_score()

        # 首次放置食物
        self.food.respawn(set(self.snake.segments))

    def init_game(self):
        """重置游戏至初始状态（保留最高分）。"""
        self.snake.reset()
        self.score = 0
        self.speed = BASE_SPEED
        self.game_over_flag = False
        self.paused = False
        self.food.respawn(set(self.snake.segments))

    def _load_high_score(self):
        """从 JSON 文件加载历史最高分。

        处理文件不存在或 JSON 格式错误的情况，返回 0 作为默认值。

        返回:
            int: 历史最高分。
        """
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return json.load(f).get("high_score", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            # 首次运行或文件损坏时，最高分默认为 0
            return 0

    def _save_high_score(self):
        """将当前最高分写入 JSON 文件持久化保存。"""
        with open(HIGH_SCORE_FILE, "w") as f:
            json.dump({"high_score": self.high_score}, f)

    def set_direction(self, dx, dy):
        """委托给 Snake 对象设置移动方向。

        参数:
            dx: 水平方向分量。
            dy: 垂直方向分量。
        """
        self.snake.set_direction(dx, dy)

    def toggle_pause(self):
        """切换暂停/继续状态，游戏结束时不可暂停。"""
        if self.game_over_flag:
            return
        self.paused = not self.paused

    def step(self):
        """执行一帧游戏逻辑：移动蛇、检测碰撞、处理吃食物。

        暂停或游戏结束状态下不执行任何逻辑。
        """
        if self.game_over_flag or self.paused:
            return

        # 预测下一步是否会吃到食物，以决定是否生长
        next_head = (self.snake.head[0] + self.snake.next_direction[0],
                     self.snake.head[1] + self.snake.next_direction[1])
        grow = next_head == self.food.position
        new_head = self.snake.move(grow=grow)

        # 边界碰撞检测
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            self._game_over()
            return

        # 自身碰撞检测
        if self.snake.collides_with_self():
            self._game_over()
            return

        # 吃到食物：加分、加速、生成新食物
        if new_head == self.food.position:
            self.score += POINTS_PER_FOOD
            self.speed = max(MIN_SPEED, self.speed - SPEED_INCREMENT)
            if not self.food.respawn(set(self.snake.segments)):
                # 无空闲格子，玩家胜利
                self._win()

    def _game_over(self):
        """处理游戏失败：标记结束，若破纪录则保存最高分。"""
        self.game_over_flag = True
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    def _win(self):
        """处理玩家胜利：标记结束，若破纪录则保存最高分。"""
        self.game_over_flag = True
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    def draw(self):
        """绘制游戏全部画面：网格、食物、蛇、状态栏、覆盖层。

        绘制顺序：背景 → 网格 → 食物 → 蛇 → 底部信息栏 → 弹窗覆盖层。
        """
        # 清屏
        self.screen.fill(BG_COLOR)

        # 绘制网格线
        for x in range(COLS):
            for y in range(ROWS):
                rect = pygame.Rect(
                    x * CELL_SIZE, y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, GRID_COLOR, rect, GRID_WIDTH)

        # 委托 Food 对象绘制食物（含光晕）
        self.food.draw(self.screen)

        # 绘制蛇身：蛇头异色 + 眼睛，身体段由头到尾渐变色
        for i, (sx, sy) in enumerate(self.snake.segments):
            x = sx * CELL_SIZE + 1
            y = sy * CELL_SIZE + 1
            w = CELL_SIZE - 2

            if i == 0:
                color = SNAKE_HEAD_COLOR
            else:
                # 线性插值实现身体颜色渐变
                t = i / max(len(self.snake.segments) - 1, 1)
                r_val = int(SNAKE_BODY_START[0] + t * (SNAKE_BODY_END[0] - SNAKE_BODY_START[0]))
                g_val = int(SNAKE_BODY_START[1] + t * (SNAKE_BODY_END[1] - SNAKE_BODY_START[1]))
                b_val = int(SNAKE_BODY_START[2] + t * (SNAKE_BODY_END[2] - SNAKE_BODY_START[2]))
                color = (r_val, g_val, b_val)

            radius = 6 if i == 0 else 4
            pygame.draw.rect(self.screen, color, (x, y, w, w), border_radius=radius)

            # 蛇头绘制白色眼睛，方向决定眼睛位置
            if i == 0:
                eye_size = 3
                eye_color = (255, 255, 255)
                mid_x, mid_y = x + w // 2, y + w // 2
                dx, dy = self.snake.direction
                if dx == 1:      # 向右
                    pygame.draw.rect(self.screen, eye_color, (mid_x + 3, mid_y - 5, eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, (mid_x + 3, mid_y + 2, eye_size, eye_size))
                elif dx == -1:    # 向左
                    pygame.draw.rect(self.screen, eye_color, (mid_x - 6, mid_y - 5, eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, (mid_x - 6, mid_y + 2, eye_size, eye_size))
                elif dy == -1:    # 向上
                    pygame.draw.rect(self.screen, eye_color, (mid_x - 5, mid_y - 6, eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, (mid_x + 2, mid_y - 6, eye_size, eye_size))
                elif dy == 1:     # 向下
                    pygame.draw.rect(self.screen, eye_color, (mid_x - 5, mid_y + 3, eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, (mid_x + 2, mid_y + 3, eye_size, eye_size))

        # 底部信息栏
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

        # 游戏结束/胜利覆盖层
        if self.game_over_flag:
            overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))

            go_font = pygame.font.SysFont("microsoftyahei", 48, bold=True)
            # 食物为 None 且蛇占满全图 → 胜利；否则失败
            if self.food.position is None and len(self.snake.segments) == COLS * ROWS:
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

        # 暂停覆盖层
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

        # 初始待机提示（蛇处于初始位置且未移动时）
        elif not self.game_over_flag and self.snake.segments == [(COLS // 2, ROWS // 2), (COLS // 2 - 1, ROWS // 2), (COLS // 2 - 2, ROWS // 2)]:
            tip = self.font_small.render("按 方向键/WASD 开始", True, (120, 120, 120))
            tip_rect = tip.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 60))
            self.screen.blit(tip, tip_rect)

        # 刷新显示
        pygame.display.flip()

    def run(self):
        """游戏主循环：事件处理 → 逻辑更新 → 渲染，按 speed 控制帧率。"""
        while self.running:
            self._handle_events()
            if not self.paused and not self.game_over_flag:
                self.step()
            self.draw()
            # 使用毫秒控制：speed 越小越快
            self.clock.tick(1000 // self.speed)

    def _handle_events(self):
        """处理 pygame 事件队列：退出、键盘输入。

        方向键/WASD → 移动，空格 → 暂停，R → 重开，Q → 退出。
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_over_flag:
                    # 游戏结束后的按键处理
                    if event.key == pygame.K_r:
                        self.init_game()
                    elif event.key == pygame.K_q:
                        self.running = False
                elif event.key == pygame.K_SPACE:
                    self.toggle_pause()
                elif not self.paused:
                    # 方向输入
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.set_direction(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.set_direction(0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.set_direction(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.set_direction(1, 0)
