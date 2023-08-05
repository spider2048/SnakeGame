import pygame as pg
import enum
import logging
import random

logging.basicConfig(level=logging.DEBUG)


class Direction(enum.Enum):
    up = pg.K_UP
    down = pg.K_DOWN
    left = pg.K_LEFT
    right = pg.K_RIGHT


class Snake:
    def __init__(self, bounds, width, surface):
        logging.debug(f"snake.__init__ with bounds: {bounds}")
        self.boxes = [
            [0, 0, Direction.right],
        ]

        self.rects: list[pg.Rect] = []
        self.bait_rect = None
        self.bait = None

        self.xbound, self.ybound = bounds
        self.box_size = width

        self.alive = True

        self.border_color = (255, 0, 0)
        self.body_color = (255, 255, 0)
        self.bait_color = (0, 255, 133)

        self.surface = surface

        self.prev_moved = 0
        self.move_delay = 100

        self.is_rendered = False

        self._vertical_set = set((Direction.up, Direction.down))
        self._horizontal_set = set((Direction.left, Direction.right))

    def move(self):
        self.is_rendered = False
        for i in range(len(self.boxes)):
            x, y, d = self.boxes[i]
            match d:
                case Direction.up:
                    if y == 0:
                        self.boxes[i][1] = self.ybound
                    else:
                        self.boxes[i][1] -= self.box_size

                case Direction.down:
                    if y + self.box_size == self.ybound:
                        self.boxes[i][1] = 0
                    else:
                        self.boxes[i][1] += self.box_size

                case Direction.left:
                    if x == 0:
                        self.boxes[i][0] = self.xbound
                    else:
                        self.boxes[i][0] -= self.box_size

                case Direction.right:
                    if x + self.box_size == self.xbound:
                        self.boxes[i][0] = 0
                    else:
                        self.boxes[i][0] += self.box_size

        prev_direction = self.boxes[0][2]
        for i in range(1, len(self.boxes)):
            self.boxes[i][2], prev_direction = prev_direction, self.boxes[i][2]

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
            logging.error(f"snake is dead!")
            self.alive = False

    def turn(self, direction: Direction):
        x, y, d = self.boxes[0]
        if x >= self.xbound or y >= self.ybound:
            return

        direction_set = set((d, direction))
        if direction_set == self._vertical_set or direction_set == self._horizontal_set:
            logging.debug(f"prevented from coming back")
            return

        self.boxes[0][2] = direction

    def eat(self):
        self.is_rendered = False
        x, y, d = self.boxes[-1]
        match d:
            case Direction.up:
                self.boxes.append([x, y + self.box_size, d])
            case Direction.down:
                self.boxes.append([x, y - self.box_size, d])
            case Direction.left:
                self.boxes.append([x + self.box_size, y, d])
            case Direction.right:
                self.boxes.append([x - self.box_size, y, d])

    def render(self):
        if self.is_rendered:
            return

        self.rects.clear()
        self.is_rendered = True
        self.surface.fill("black")
        for x, y, _ in self.boxes:
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
            random.randint(0, self.xbound),
            random.randint(0, self.ybound),
        )
        logging.debug(f"bait.spawn at {self.bait}")
        self.is_rendered = False

    def despawn_bait(self):
        self.is_rendered = False
        self.bait = None
        self.bait_rect = None


class Game:
    def __init__(self):
        pg.init()

        self.width = 900
        self.height = 700

        self.running = False
        self.screen = pg.display.set_mode((self.width, self.height))

        self.box_size = 50
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
                        pg.quit()
                        quit()

                    if event.type == pg.KEYDOWN:
                        match event.key:
                            case pg.K_UP:
                                self.snake.turn(Direction.up)
                            case pg.K_DOWN:
                                self.snake.turn(Direction.down)
                            case pg.K_LEFT:
                                self.snake.turn(Direction.left)
                            case pg.K_RIGHT:
                                self.snake.turn(Direction.right)

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
                    pg.quit()
                    quit()
                wait = not (ev.type == pg.KEYDOWN and ev.key == pg.K_r)


g = Game()
g.mainloop()
