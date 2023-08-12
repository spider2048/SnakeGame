import enum
import logging
import sys
import random

import pygame as pg
from pygame import Vector2 as Vec2
logging.basicConfig(level=logging.DEBUG)


class Direction(enum.Enum):
    UP = Vec2(0, 1)
    DOWN = Vec2(0, -1)
    LEFT = Vec2(-1, 0)
    RIGHT = Vec2(1, 0)


class Snake:
    def __init__(self, bounds, width, surface):
        logging.debug("snake.__init__ with bounds: %s", bounds)

        self.pos = [Vec2(0, 0)]
        self.dirs = [Direction.RIGHT]

        self.rects: list[pg.Rect] = []
        self.bait_rect = None
        self.bait = None

        self.xbound, self.ybound = bounds
        self.box_size = width

        self.alive = True

        self.border_color = (255, 0, 0)
        self.body_color = (255, 255, 0)
        self.bait_color = (0, 100, 0)

        self.surface = surface

        self.prev_moved = 0
        self.move_delay = 15

        self._vertical_set = set((Direction.UP, Direction.DOWN))
        self._horizontal_set = set((Direction.LEFT, Direction.RIGHT))

    def move(self):
        for i, (pos, d) in enumerate(zip(self.pos, self.dirs)):
            match d:
                case Direction.UP:
                    if pos.y <= 0:
                        pos.y = self.ybound
                    else:
                        pos.y -= self.box_size

                case Direction.DOWN:
                    if pos.y + self.box_size >= self.ybound:
                        pos.y = 0
                    else:
                        pos.y += self.box_size

                case Direction.LEFT:
                    if pos.x <= 0:
                        pos.x = self.xbound
                    else:
                        pos.x -= self.box_size

                case Direction.RIGHT:
                    if pos.x + self.box_size >= self.xbound:
                        pos.x = 0
                    else:
                        pos.x += self.box_size

        prev_direction = self.dirs[0]
        for i in range(1, len(self.dirs)):
            self.dirs[i], prev_direction = prev_direction, self.dirs[i]

        self.prev_moved = pg.time.get_ticks()

    def tick(self):
        if not self.bait:
            self.spawn_bait()

        if pg.time.get_ticks() - self.prev_moved > self.move_delay:
            self.move()

        self.check_hit()
        self.render()

    def check_hit(self):
        if self.bait_rect and self.bait_rect.colliderect(self.rects[0]):
            logging.debug("snake.check_hit hit")
            self.eat()
            self.despawn_bait()

        if self.rects and any(self.rects[0].collidelistall(self.rects[1:])):
            logging.error("snake is dead!")
            self.alive = False

    def turn(self, direction: Direction):
        ip = self.pos[0]
        if ip.x >= self.xbound or ip.y >= self.ybound:
            return

        direction_set = set((self.dirs[0], direction))
        if direction_set in (self._vertical_set, self._horizontal_set):
            logging.debug("prevented from coming back")
            return

        self.dirs[0] = direction

    def eat(self):
        x, y = self.pos[-1]
        match self.dirs[-1]:
            case Direction.UP:
                self.pos.append(Vec2(x, y + self.box_size))
            case Direction.DOWN:
                self.pos.append(Vec2(x, y - self.box_size))
            case Direction.LEFT:
                self.pos.append(Vec2(x + self.box_size, y))
            case Direction.RIGHT:
                self.pos.append(Vec2(x - self.box_size, y))
        
        self.dirs.append(self.dirs[-1])

    def render(self):        
        self.rects.clear()
        self.surface.fill("green")
        for x, y in self.pos:
            pg.draw.rect(
                self.surface,
                self.body_color,
                (
                    x,
                    y,
                    self.box_size,
                    self.box_size,
                ),
            )

            rb = pg.draw.rect(
                self.surface,
                self.border_color,
                (
                    x,
                    y,
                    self.box_size,
                    self.box_size,
                ),
                width=3,
            )

            self.rects.append(rb)

        if self.bait:
            self.bait_rect = pg.draw.rect(
                self.surface,
                self.bait_color,
                (self.bait[0], self.bait[1], self.box_size, self.box_size),
            )

    def spawn_bait(self):
        self.bait = (
            random.randint(0, self.xbound - self.box_size),
            random.randint(0, self.ybound - self.box_size),
        )

        logging.debug("bait.spawn at %s", self.bait)

    def despawn_bait(self):
        self.bait = None
        self.bait_rect = None


class Game:
    def __init__(self):
        pg.init()

        self.width = 900
        self.height = 700

        self.running = False
        self.screen = pg.display.set_mode((self.width, self.height))

        self.box_size = 30
        self.bounds = (self.width, self.height)

        self.snake = None

        self.font = pg.font.SysFont("Comic Sans MS", 30)
        self.game_over = self.font.render(
            "Game Over! [R] to restart", False, (255, 255, 0)
        )

    def mainloop(self):
        clock = pg.time.Clock()
        self.running = True

        while self.running:
            self.snake = Snake(self.bounds, self.box_size, self.screen)
            while self.snake.alive:
                for event in pg.event.get():
                    if event.type == pg.WINDOWCLOSE:
                        self.cleanup()

                    if event.type == pg.KEYDOWN:
                        match event.key:
                            case pg.K_UP:
                                self.snake.turn(Direction.UP)
                            case pg.K_DOWN:
                                self.snake.turn(Direction.DOWN)
                            case pg.K_LEFT:
                                self.snake.turn(Direction.LEFT)
                            case pg.K_RIGHT:
                                self.snake.turn(Direction.RIGHT)

                self.snake.tick()
                clock.tick(60)
                pg.display.flip()

            self.screen.blit(
                self.game_over,
                (
                    self.width // 2 - self.game_over.get_width() // 2,
                    self.height // 2 - self.game_over.get_height() // 2,
                ),
            )
            pg.display.flip()

            wait = True
            while wait:
                ev = pg.event.wait()
                if ev.type == pg.WINDOWCLOSE:
                    self.cleanup()
                wait = not (ev.type == pg.KEYDOWN and ev.key == pg.K_r)

    @staticmethod
    def cleanup():
        pg.quit()
        sys.exit(0)

if __name__ == '__main__':
    g = Game()
    g.mainloop()
