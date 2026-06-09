# 贪吃蛇 (Pygame 版)

> **仓库地址**: [https://github.com/1lya-bit/snake-pygame](https://github.com/1lya-bit/snake-pygame)

## 项目简介
使用 Python + pygame 实现的经典贪吃蛇游戏。

## 环境要求
- Python 3.8+
- pygame 2.0+

## 安装与运行

### 1. 安装依赖
```bash
pip install pygame
```

### 2. 运行游戏
```bash
python main.py
```

## 操作说明

| 按键 | 功能 |
|------|------|
| ↑ ↓ ← → / WASD | 控制蛇的移动方向 |
| 空格 | 暂停 / 继续 |
| R | 游戏结束后重新开始 |
| Q | 游戏结束后退出 |

## 游戏规则
- 控制蛇吃到红色的食物，每吃一个加 10 分
- 蛇撞到墙壁或自己的身体则游戏结束
- 随着分数增加，蛇的移动速度逐渐加快
- 最高分会自动保存到本地文件

## 项目结构
```
snake-pygame/
├── main.py          # 程序入口
├── game.py          # 游戏主控制器（SnakeGame）
├── snake.py         # 蛇实体类（Snake）
├── food.py          # 食物实体类（Food）
├── settings.py      # 配置常量
└── README.md        # 本文件
```

### 面向对象设计
- **SnakeGame** — 游戏主控，管理循环、事件、渲染调度
- **Snake** — 封装蛇身坐标、移动方向、碰撞检测
- **Food** — 封装食物随机放置与光晕绘制