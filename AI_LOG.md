# AI 辅助开发日志 (AI_LOG.md)

> **项目名称**: 贪吃蛇 (Snake Pygame)  
> **AI 工具**: Claude (Anthropic)  
> **开发周期**: 2026-06-01 ~ 2026-06-09  
> **团队成员**: (填写姓名)

---

## 目录

1. [使用的 AI 工具](#1-使用的-ai-工具)
2. [提示词记录](#2-提示词记录)
3. [反思与收获](#3-反思与收获)

## 1. 使用的 AI 工具

| 工具 | 用途 |
|------|------|
| **deepseek** (Anthropic) | 全部代码生成、调试、重构、文档编写 |

## 2. 提示词记录

共记录 **10 条**有效提示词，覆盖环境配置、核心功能实现、错误调试、数据存储与可视化四个方面。

---

### 类别一：环境配置

---

#### 提示词 #1

**类型**: 环境配置  
**日期**: 2026-06-01  
**提示词**:

> 我想用 Python + pygame 做一个贪吃蛇游戏。请帮我初始化项目：创建游戏窗口（800×600），绘制网格背景，显示一个初始长度为3的蛇在画面中央。

**AI 原始输出 (关键部分)**:

```python
import pygame

# 常量定义
CELL_SIZE = 20
COLS, ROWS = 40, 30
WINDOW_W = COLS * CELL_SIZE
WINDOW_H = ROWS * CELL_SIZE + 60

pygame.init()
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("贪吃蛇 - Snake")
```

**人工修改说明**:
- 理解了 `CELL_SIZE`、`COLS`、`ROWS` 之间的关系：窗口尺寸 = 网格列数 × 单元格大小
- 手动调整了 `WINDOW_H` 额外加 60px 用于底部信息栏
- 自己编写了 `.gitignore`（排除 `__pycache__`、`.idea`）
- 理解了 `pygame.display.set_mode()` 和 `set_caption()` 的作用

#### 提示词 #2

**类型**: 环境配置  
**日期**: 2026-06-01  
**提示词**:

> 项目的 settings.py 应该包含哪些配置常量？请列出贪吃蛇游戏需要的所有常量和颜色定义。

**AI 原始输出 (关键部分)**:

```python
# 窗口
CELL_SIZE = 20
COLS, ROWS = 40, 30
WINDOW_W = COLS * CELL_SIZE
WINDOW_H = ROWS * CELL_SIZE + 60

# 速度
BASE_SPEED = 8
MIN_SPEED = 2
SPEED_INCREMENT = 0.5
POINTS_PER_FOOD = 10

# 颜色
BG_COLOR = (15, 15, 35)
GRID_COLOR = (30, 30, 50)
SNAKE_HEAD_COLOR = (0, 200, 83)
SNAKE_BODY_START = (50, 180, 80)
SNAKE_BODY_END = (20, 100, 40)
FOOD_COLOR = (255, 80, 80)
TEXT_COLOR = (220, 220, 220)
ACCENT_COLOR = (255, 200, 0)
```

**人工修改说明**:
- 理解了速度系统的设计：`BASE_SPEED` 是初始速度，`SPEED_INCREMENT` 控制加速幅度
- 颜色我尝试调了几版，最终采用深蓝背景 + 绿色蛇 + 红色食物的经典配色
- `SNAKE_BODY_START` → `SNAKE_BODY_END` 的渐变需要用 RGB 插值，这部分算法我理解了

### 类别二：核心功能实现


#### 提示词 #3

**类型**: 核心功能实现  
**日期**: 2026-06-02  
**提示词**:

> 请实现贪吃蛇的移动功能：按方向键/WASD 控制方向，蛇自动向前移动。特别要注意：禁止反向移动（例如向右移动时不能直接按左键掉头），否则蛇会撞到自己。

**AI 原始输出 (关键部分)**:

```python
def set_direction(self, dx, dy):
    # 禁止反向：当前向右(1,0)则禁止向左(-1,0)
    if (dx, dy) == (-self.direction[0], -self.direction[1]):
        return
    self.next_direction = (dx, dy)

def move(self, grow=False):
    self.direction = self.next_direction
    head_x, head_y = self.head
    new_head = (head_x + self.direction[0],
                head_y + self.direction[1])
    self.segments.insert(0, new_head)
    if not grow:
        self.segments.pop()
    return new_head
```

**人工修改说明**:
- **防反向逻辑的核心**：`(-self.direction[0], -self.direction[1])` 算出当前方向的相反方向，如果新方向等于反方向则忽略——这个数学表达很巧妙，我花时间完全理解了
- `next_direction` 缓冲机制：方向先存到 `next_direction`，每帧 `move()` 时才正式应用，避免了同一帧内多次改变方向导致的问题
- `grow` 参数控制是否生长：吃到食物 `grow=True` 时不 pop 尾部，长度+1

---

#### 提示词 #4

**类型**: 核心功能实现  
**日期**: 2026-06-07  
**提示词**:

> 请实现食物系统：食物随机出现在空格子上（不能和蛇身重叠），蛇吃到食物后加分并加速，同时生成新食物。当网格被占满时判定玩家胜利。包含边界碰撞和自身碰撞检测。

**AI 原始输出 (关键部分)**:

```python
def respawn(self, occupied):
    available = [(x, y) for x in range(COLS) 
                 for y in range(ROWS) 
                 if (x, y) not in occupied]
    if not available:
        self.position = None  # 胜利条件
        return False
    self.position = random.choice(available)
    return True

# 碰撞检测
if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
    self._game_over()
if self.snake.collides_with_self():
    self._game_over()
```

**人工修改说明**:
- 食物生成用了**列表推导式**枚举所有空闲格子，然后 `random.choice` 随机选——时间复杂度 O(n)，对于 40×30 网格完全够用
- `self.position = None` 作为胜利标志的设计很简洁，在渲染时直接跳过绘制
- 边界碰撞：`new_head` 的 x 坐标 [0, COLS) 区间判断，y 同理
- 自身碰撞：`self.head in self.segments[1:]` ——用 `in` 运算符检查蛇头是否在身体段列表中

---

#### 提示词 #5

**类型**: 核心功能实现  
**日期**: 2026-06-08  
**提示词**:

> 请为贪吃蛇添加暂停/重开功能和最高分保存系统。按空格暂停，游戏结束后按 R 重开，按 Q 退出。最高分用 JSON 文件保存在本地，启动时自动加载。

**AI 原始输出 (关键部分)**:

```python
# 状态管理
def toggle_pause(self):
    if self.game_over_flag:
        return
    self.paused = not self.paused

# JSON 持久化
def _load_high_score(self):
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return json.load(f).get("high_score", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def _save_high_score(self):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump({"high_score": self.high_score}, f)
```

**人工修改说明**:
- **游戏状态的互斥**：`paused` 和 `game_over_flag` 不能同时为 True，游戏结束时按空格不会触发暂停——我在 `toggle_pause` 里加了 `if self.game_over_flag: return`
- JSON 异常处理：捕获 `FileNotFoundError`（首次运行）和 `json.JSONDecodeError`（文件损坏），返回默认值 0——这是防御性编程的体现
- 破纪录逻辑：只有当 `score > high_score` 时才写入，避免不必要的 I/O
- 自己添加了 `init_game()` 方法，重置蛇、分数、速度但不重置最高分

---

#### 提示词 #6

**类型**: 核心功能实现  
**日期**: 2026-06-09  
**提示词**:

> 请把贪吃蛇项目中的 Snake 和 Food 拆分成独立的类文件（snake.py 和 food.py），添加完整的 docstring 注释，并更新 README 项目结构说明。

**AI 原始输出 (关键部分)**:

```python
class Snake:
    """贪吃蛇实体，管理蛇身的坐标序列与移动方向。

    属性:
        segments: 蛇身段坐标列表，首元素为蛇头。
        direction: 当前实际移动方向 (dx, dy)。
        next_direction: 缓冲的下一帧方向，防止同帧内反向掉头。
    """

    @property
    def head(self):
        """返回蛇头坐标 (x, y)。"""
        return self.segments[0]
```

```python
class Food:
    """食物实体，负责随机放置与光晕渲染。

    属性:
        position: 食物坐标 (x, y) 或 None（无空闲格子时）。
    """
```

**人工修改说明**:
- 理解了**封装原则**：Snake 只管理自己的坐标和方向，Food 只管理自己的位置和渲染，互不干扰
- `@property` 装饰器的作用：让 `head` 可以像属性一样访问（`snake.head` 而不是 `snake.head()`）
- docstring 格式：采用 Google 风格的"属性/参数/返回"三段式注释，方便阅读
- 拆文件后 `import` 关系变清晰：`game.py` 导入 `snake.py` 和 `food.py`，两者都依赖 `settings.py`

---

### 类别三：错误调试

---

#### 提示词 #7

**类型**: 错误调试  
**日期**: 2026-06-9  
**提示词**:

> 我的贪吃蛇游戏在中文 Windows 系统上运行时，按 WASD 键完全没有反应，但方向键可以正常使用。pygame 的 KEYDOWN 事件似乎没有触发。这是什么原因？如何解决？

**AI 原始输出**:

```
这是因为中文输入法处于激活状态时，IME（输入法编辑器）会拦截
WASD 字母键的按键事件，导致 pygame 无法接收到 KEYDOWN 事件。
方向键不受影响，因为它们不是输入法处理的键。

解决方法：
1. 按 Shift 键切换到英文输入模式（任务栏显示"英/ENG"）
2. 或者在游戏初始化时设置 pygame 的 IME 禁用
3. 也可以在代码中添加提示，告知玩家切换输入法
```

**人工修改说明**:
- 理解了 IME 的工作原理：中文输入法优先捕获字母键用于拼音输入，所以 pygame 的 `pygame.KEYDOWN` 收不到 WASD
- 方向键不受影响是因为它们不是文字输入键，不会被 IME 拦截
- 我在代码初始界面添加了提示文字 "按 方向键/WASD 开始"

### 类别四：数据存储与可视化
---

#### 提示词 #8

**类型**: 数据存储  
**日期**: 2026-06-08  
**提示词**:

> Python 中用 JSON 保存游戏数据时，如何处理文件不存在、JSON 格式损坏等异常？请给出一个健壮的读写方案，包括异常处理和默认值逻辑。

**AI 原始输出 (关键部分)**:

```python
def load_high_score():
    try:
        with open("high_score.json", "r") as f:
            data = json.load(f)
            return data.get("high_score", 0)
    except FileNotFoundError:
        return 0
    except json.JSONDecodeError:
        return 0

def save_high_score(score):
    try:
        with open("high_score.json", "w") as f:
            json.dump({"high_score": score}, f, indent=2)
    except IOError as e:
        print(f"保存失败: {e}")
```

**人工修改说明**:
- `json.load(f)` vs `json.loads(s)`：前者读文件对象，后者读字符串
- `data.get("high_score", 0)`：用 `.get()` 代替 `data["high_score"]`，防止 KeyError
- `indent=2` 参数让 JSON 文件格式化输出，方便人工查看
- 异常分层处理：先判断文件存不存在（`FileNotFoundError`），再判断内容是否合法（`JSONDecodeError`）
- 理解了"默认值模式"：任何异常都返回 0，程序不会因高分文件问题而崩溃
---

#### 提示词 #9

**类型**: 可视化  
**日期**: 2026-06-09  
**提示词**:

> 贪吃蛇的界面太单调了，请帮我美化：1) 蛇头用不同颜色并画出跟随方向的白色眼睛 2) 身体从蛇头到蛇尾做颜色渐变 3) 食物周围加光晕效果 4) 底部加半透明信息栏显示分数和速度 5) 蛇身用圆角矩形

**AI 原始输出 (关键部分)**:

```python
# 身体渐变（RGB 线性插值）
t = i / max(len(self.snake.segments) - 1, 1)
r_val = int(SNAKE_BODY_START[0] + t * (SNAKE_BODY_END[0] - SNAKE_BODY_START[0]))
g_val = int(SNAKE_BODY_START[1] + t * (SNAKE_BODY_END[1] - SNAKE_BODY_START[1]))
b_val = int(SNAKE_BODY_START[2] + t * (SNAKE_BODY_END[2] - SNAKE_BODY_START[2]))
color = (r_val, g_val, b_val)

# 蛇眼随方向变化
if dx == 1:      # 向右
    pygame.draw.rect(screen, WHITE, (mid_x + 3, mid_y - 5, 3, 3))
    pygame.draw.rect(screen, WHITE, (mid_x + 3, mid_y + 2, 3, 3))
elif dx == -1:   # 向左
    pygame.draw.rect(screen, WHITE, (mid_x - 6, mid_y - 5, 3, 3))
    pygame.draw.rect(screen, WHITE, (mid_x - 6, mid_y + 2, 3, 3))
# ... 上下同理
```

```python
# 食物光晕：多层半透明圆叠加
for i in range(3, 0, -1):
    alpha = 60 // i
    glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*FOOD_COLOR, alpha), 
                       (glow_size//2, glow_size//2), glow_size//2)
    screen.blit(glow_surf, (x - glow_size//2, y - glow_size//2))
```

**人工修改说明**:
- **RGB 线性插值**：`t` 从 0（蛇头后）到 1（蛇尾），`start + t * (end - start)` 完成三个通道的独立过渡，实现平滑渐变色
- **蛇眼定位**：以蛇头中心为基准，根据方向偏移——眼睛画在蛇的"前方"，朝向即运动方向
- **光晕原理**：`pygame.SRCALPHA` 创建支持透明度的 Surface，多层不同透明度的圆叠加产生柔和的发光效果
- 圆角矩形 `border_radius` 是 pygame 2.0+ 的新特性
- 半透明覆盖层用于暂停/结束遮罩：`fill((0, 0, 0, 140))` 第四个值是 alpha 通道

---

## 3. 反思与收获

### AI 帮助解决的问题

1. **快速原型搭建**：从零到能玩的贪吃蛇，AI 在不到30分钟内完成了基础框架（如果完全手写可能需要2-3小时）
2. **边界条件处理**：AI 对防反向掉头、边界碰撞、自身碰撞等逻辑的处理很全面，没有遗漏
3. **JSON 异常安全**：AI 提供的 `try-except` 多异常捕获方案让我学到了防御性编程
4. **视觉效果实现**：RGB 插值渐变、多层透明光晕等算法，AI 给出了可直接使用的代码
5. **代码规范**：docstring 格式、模块拆分、命名规范等，AI 的输出就是很好的范例

### AI 的局限性

1. **理解业务场景有限**：AI 不知道中文 Windows 的输入法问题，直到我遇到 bug 主动提问才给出方案
2. **代码需要人工验证**：AI 生成的碰撞检测顺序（先边界后自身）如果颠倒可能导致 IndexError，需要人工审查
3. **不会主动建议最佳实践**：最初的代码全部写在 `game.py`，是我主动要求重构才拆分模块
4. **无法判断需求合理性**：我如果说"让蛇能穿墙"，AI 会直接实现，但不会告诉我这破坏了游戏性

### 个人收获

1. 通过逐行理解 AI 代码，我对 **pygame 事件循环**和**游戏状态机**有了深刻理解
2. 学会了 **RGB 颜色插值**、**透明 Surface** 等图形编程技巧
3. 掌握了 **JSON 持久化** 的异常安全写法
4. 真正理解了**面向对象封装**：不是简单拆文件，而是让每个类"管好自己的事"
5. 认识到 **AI 是助手不是替代品**——代码可以生成，但理解、验证、优化必须自己来