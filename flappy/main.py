#!/usr/bin/env python

from __future__ import annotations

import pygame
import random
import enum
from dataclasses import dataclass
from collections import deque


C_BLUE = (85, 205, 252)
C_PINK = (247, 168, 184)
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)

G_GAP = 1 / 5
G_GAP_RAND = 1 / 6
G_PIPE_WIDTH = 1 / 8
G_SPEED = 1 / 4
G_SPACE = 1 / 3
G_JUMP = 1 / 2
G_ACC = 1


class HorzRel(enum.Enum):
    """
    Fields
    ----------
    LEFT: -1
    BETWEEN: 0
    RIGHT: 1
    """
    LEFT = -1
    BETWEEN = 0
    RIGHT = 1


@dataclass
class Vec:
    x: float
    y: float

    def cross(self, other: Vec) -> float:
        return self.x * other.y - self.y * other.x

    def dot(self, other: Vec) -> float:
        return self.x * other.x + self.y + other.y

    def scale(self, factor: float) -> Vec:
        return Vec(self.x * factor, self.y * factor)

    def __sub__(self, other: Vec) -> Vec:
        return Vec(self.x - other.x, self.y - other.y)

    def __add__(self, other: Vec) -> Vec:
        return Vec(self.x + other.x, self.y + other.y)


def edge(v0: Vec, v1: Vec, point: Vec) -> float:
    """
    Calculate point relation to edge from v0 to v1.

    Parameters
    ----------
    v0: Vec
        first edge point.
    v1: Vec
        Second edge point.
    point: Vec
        Point to compare to edge


    Returns
    -------
    float
        Zero: on edge.
        Positive: right side of edge.
        Negative: left side of edge.
    """
    a = point - v0
    b = point - v1

    return a.cross(b)


class Rect:

    def __init__(self, pos: Vec, dim: Vec):
        self.pos = pos
        self.dim = dim

        self.v0 = pos
        self.v1 = Vec(pos.x + dim.x, pos.y)
        self.v2 = Vec(pos.x + dim.x, pos.y + dim.y)
        self.v3 = Vec(pos.x, pos.y + dim.y)

    @staticmethod
    def gen_random_pipe_set(posx: int, gap: int, w: int, h: int) -> tuple[Rect, Rect]:
        gap_place_h = random.randint(int(h * G_GAP_RAND), h - 2 * int(h * G_GAP_RAND))
        r1 = Rect(pos=Vec(posx, 0), dim=Vec(w * G_PIPE_WIDTH, gap_place_h))
        r2 = Rect(pos=Vec(posx, gap_place_h + gap), dim=Vec(w * G_PIPE_WIDTH, h - gap_place_h))

        return (r1, r2)

    def occupies_pos(self, pos: Vec) -> bool:
        e10 = edge(self.v1, self.v0, pos)
        e21 = edge(self.v2, self.v1, pos)
        e32 = edge(self.v3, self.v2, pos)
        e03 = edge(self.v0, self.v3, pos)

        if e10 <= 0 and e21 <= 0 and e32 <= 0 and e03 <= 0:
            return True

        return False

    def get_horz_rel(self, point: Vec) -> HorzRel:
        e03 = edge(self.v0, self.v3, point)
        if e03 >= 0:
            return HorzRel.LEFT

        e21 = edge(self.v2, self.v1, point)
        if e21 >= 0:
            return HorzRel.RIGHT

        return HorzRel.BETWEEN

    def draw(self, window: pygame.surface.Surface) -> None:
        pygame.draw.rect(window,
                         C_BLUE,
                         (int(self.pos.x), int(self.pos.y), int(self.dim.x), int(self.dim.y)))

    def loop(self, speed: int, dt: float) -> None:
        self.pos -= Vec(speed * dt, 0)

        self.v0 = self.pos
        self.v1 = Vec(self.pos.x + self.dim.x, self.pos.y)
        self.v2 = Vec(self.pos.x + self.dim.x, self.pos.y + self.dim.y)
        self.v3 = Vec(self.pos.x, self.pos.y + self.dim.y)


@dataclass
class Bird:
    pos: Vec
    vel: Vec
    acc: Vec

    def jump(self, w_height: int) -> None:
        self.vel.y = - (w_height * G_JUMP)

    def draw(self, window: pygame.surface.Surface) -> None:
        pygame.draw.circle(window, C_PINK, (int(self.pos.x), int(self.pos.y)), 25)

    def _update_vel(self, dt: float) -> None:
        # TODO: add air resistance
        self.vel += self.acc.scale(dt)

    def _update_pos(self, dt: float) -> None:
        self.pos += self.vel.scale(dt)

    def loop(self, dt: float) -> None:
        self._update_vel(dt)
        self._update_pos(dt)


class Game:

    def __init__(self, w: int, h: int) -> None:
        self.bird = Bird(pos=Vec(w / 6, 80), vel=Vec(0, -20), acc=Vec(0, h * G_ACC))
        self.score = 0
        self.speed = int(w * G_SPEED)
        self.pipes: deque[Rect] = deque()
        return None

    def reset(self, w: int, h: int) -> None:
        self.bird = Bird(pos=Vec(w / 6, 80), vel=Vec(0, -20), acc=Vec(0, h * G_ACC))
        self.score = 0
        self.pipes = deque()

    def add_pipe_set(self, w: int, h: int) -> None:
        if len(self.pipes) == 0:
            x_pos = w - w / 5
        else:
            x_pos = self.pipes[-1].pos.x + w * G_SPACE
        r1, r2 = Rect.gen_random_pipe_set(int(x_pos), int(h * G_GAP), w, h)
        self.pipes.append(r1)
        self.pipes.append(r2)
        return None

    def update_vars(self, dt: float) -> None:
        self.bird.loop(dt)
        for pipe in self.pipes:
            pipe.loop(self.speed, dt)

    def draw(self, window: pygame.surface.Surface) -> None:
        self.bird.draw(window)
        for pipe in self.pipes:
            pipe.draw(window)

    def clean_pipes(self) -> int:
        pops = 0
        for pipe in self.pipes:
            if pipe.get_horz_rel(Vec(0, 0)) == HorzRel.RIGHT:
                pops += 1
                continue
            break

        for i in range(pops):
            self.pipes.popleft()

        return pops // 2

    def is_colliding(self, height: int) -> bool:
        if self.bird.pos.y > height or self.bird.pos.y < 0:
            return True
        for pipe in self.pipes:
            relation = pipe.get_horz_rel(self.bird.pos)
            match relation:
                case HorzRel.RIGHT:
                    continue
                case HorzRel.BETWEEN:
                    if pipe.occupies_pos(self.bird.pos):
                        return True
                    continue
                case HorzRel.LEFT:
                    break
        return False

    def win_res_update_vars(self, w: int, h: int) -> None:
        self.speed = int(w * G_SPEED)
        self.bird.acc.y = h * G_ACC
        return None

    def loop(self, window: pygame.surface.Surface, dt: float, w: int, h: int) -> None:
        self.update_vars(dt)
        self.score += self.clean_pipes()
        self.draw(window)

        if self.is_colliding(h):
            self.reset(w, h)

        if len(self.pipes) < 6 * 2:
            self.add_pipe_set(w, h)
        return None


def draw_trans_bg(window: pygame.surface.Surface, w: int, h: int) -> None:
    pygame.draw.rect(window, C_BLUE, (0, 0, w, h // 5))
    pygame.draw.rect(window, C_PINK, (0, h // 5, w, h // 5))
    pygame.draw.rect(window, C_WHITE, (0, 2 * (h // 5), w, h // 5))
    pygame.draw.rect(window, C_PINK, (0, 3 * (h // 5), w, h // 5))
    pygame.draw.rect(window, C_BLUE, (0, 4 * (h // 5), w, h // 5))


def draw_bg(window: pygame.surface.Surface) -> None:
    window.fill(C_WHITE)


def main() -> None:
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Firstgame')

    w_width = 800
    w_height = 500
    window = pygame.display.set_mode((w_width, w_height))

    clock = pygame.time.Clock()
    frames = 60
    dt = 1 / frames

    game_obj = Game(w_width, w_height)

    font = pygame.font.SysFont('freesans', 32)
    text = font.render(f'score: {game_obj.score}', True, (0, 0, 0))

    running = True
    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.VIDEORESIZE | pygame.FULLSCREEN:
                    w_width, w_height = window.get_size()
                    game_obj.win_res_update_vars(w_width, w_height)
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_UP | pygame.K_SPACE | pygame.K_k:
                            game_obj.bird.jump(w_height)

        draw_bg(window)
        # Update state and render game
        game_obj.loop(window, dt, w_width, w_height)

        # Show user score
        window.blit(text, (0, 0))
        text = font.render(f'score: {game_obj.score}', True, (0, 0, 0))

        pygame.display.flip()
        clock.tick(frames)

    pygame.quit()
    return None


if __name__ == '__main__':
    main()
