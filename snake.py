"""蛇实体模块。

定义 Snake 类，封装蛇的段坐标、移动方向及碰撞检测逻辑，
体现面向对象的封装原则。
"""

from settings import COLS, ROWS


class Snake:
    """贪吃蛇实体，管理蛇身的坐标序列与移动方向。

    属性:
        segments: 蛇身段坐标列表，首元素为蛇头。
        direction: 当前实际移动方向 (dx, dy)。
        next_direction: 缓冲的下一帧方向，防止同帧内反向掉头。
    """

    def __init__(self):
        """初始化蛇：位于网格中央，默认向右移动，初始长度 3。"""
        cx, cy = COLS // 2, ROWS // 2
        self.segments = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

    @property
    def head(self):
        """返回蛇头坐标 (x, y)。"""
        return self.segments[0]

    def set_direction(self, dx, dy):
        """尝试设定新方向，禁止与当前方向相反的掉头操作。

        参数:
            dx: 水平分量，-1/0/1。
            dy: 垂直分量，-1/0/1。
        """
        # 禁止反向：例如当前向右(1,0)则禁止向左(-1,0)
        if (dx, dy) == (-self.direction[0], -self.direction[1]):
            return
        self.next_direction = (dx, dy)

    def move(self, grow=False):
        """前进一步：在头部前方插入新头，若未吃食物则移除尾部。

        参数:
            grow: 是否生长（吃到食物时为 True）。

        返回:
            tuple: 新头部坐标 (nx, ny)，供外部碰撞检测使用。
        """
        # 应用缓冲方向，完成本帧移动
        self.direction = self.next_direction
        head_x, head_y = self.head
        new_head = (head_x + self.direction[0],
                    head_y + self.direction[1])

        # 新头插入段首
        self.segments.insert(0, new_head)

        if not grow:
            # 未生长则移除尾部，保持长度不变
            self.segments.pop()

        return new_head

    def collides_with_self(self):
        """检测蛇头是否与身体其他部分重叠。

        返回:
            bool: 重叠则 True。
        """
        return self.head in self.segments[1:]

    def reset(self):
        """重置蛇到初始状态（位置、方向、长度）。"""
        cx, cy = COLS // 2, ROWS // 2
        self.segments = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
