"""食物实体模块。

定义 Food 类，封装食物的随机生成与渲染逻辑。
"""

import random

import pygame
from settings import COLS, ROWS, CELL_SIZE, FOOD_COLOR


class Food:
    """食物实体，负责在空闲网格中随机放置并绘制自身。

    属性:
        position: 食物当前坐标 (x, y)，无食物时为 None。
    """

    def __init__(self):
        """初始化食物，position 为 None，待首次 respawn 调用后生效。"""
        self.position = None

    def respawn(self, occupied):
        """在未被蛇身占据的网格中随机选取一处放置食物。

        参数:
            occupied: 不可放置的坐标集合，即蛇身占据的所有格子。

        返回:
            bool: 成功放置返回 True，无可放置位置时返回 False。
        """
        # 收集所有空闲格子
        free = [(x, y) for x in range(COLS) for y in range(ROWS)
                if (x, y) not in occupied]
        if free:
            self.position = random.choice(free)
            return True
        # 无空闲格子 → 玩家胜利
        self.position = None
        return False

    def draw(self, screen):
        """在屏幕上绘制食物，含光晕效果。

        参数:
            screen: pygame 的 Surface 对象。
        """
        if self.position is None:
            return

        fx, fy = self.position
        cx = fx * CELL_SIZE + CELL_SIZE // 2
        cy = fy * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 2

        # 绘制三层光晕（由大到小，由暗到亮）
        for i in range(3, 0, -1):
            color = (255, 80 + i * 20, 80 + i * 20)
            pygame.draw.circle(screen, color, (cx, cy), r + i * 2)

        # 绘制食物本体
        pygame.draw.circle(screen, FOOD_COLOR, (cx, cy), r)
