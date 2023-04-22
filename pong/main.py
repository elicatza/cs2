#!/usr/bin/env python
import pygame
import random
import time
import enum
import math
from typing import TypedDict
from dataclasses import dataclass


# https://www.sciencecalculators.org/mechanics/collisions/


C_BLUE = (85, 205, 252)
C_PINK = (247, 168, 184)
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)


class Wall(enum.Enum):
    TOP = enum.auto()
    BOTTOM = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()
    NONE = enum.auto()


class BallState(enum.Enum):
    LOSE = enum.auto()
    BOUNCE = enum.auto()
    NONE = enum.auto()


@dataclass
class Vec:
    x: float
    y: float


@dataclass
class Pos:
    x: float
    y: float


class Rectangle(TypedDict):
    pos: Pos
    width: int
    height: int
    vel: Vec


class Ball(TypedDict):
    rad: int
    pos: Pos
    vel: Vec

    def check_wall_collition(self, w: int, h: int) -> Wall:
        if self['pos'].x < self['rad']:
            return Wall.LEFT

        if self['pos'].x > w - self['rad']:
            return Wall.RIGHT

        if self['pos'].y < self['rad']:
            return Wall.TOP

        if self['pos'].y > h - self['rad']:
            return Wall.BOTTOM

        return Wall.NONE

    # Checks rectangle not circle collition
    def check_lose_condition(self, rect: Rectangle, height: int) -> BallState:
        if self['pos'].y + self['rad'] > height:
            return BallState.LOSE

        if self['pos'].x + self['rad'] > rect['pos'].x and self['pos'].x - self['rad'] < rect['pos'].x + rect['width']:
            if self['pos'].y + self['rad'] > rect['pos'].y:
                return BallState.BOUNCE

        return BallState.NONE


def ball_handle_wall_collition(ball: Ball, wall: Wall, w: int, h: int) -> None:
    match wall:
        case Wall.RIGHT:
            ball['vel'].x *= -1
            ball['pos'].x = w - ball['rad']
        case Wall.LEFT:
            ball['vel'].x *= -1
            ball['pos'].x = ball['rad']
        case Wall.BOTTOM:
            ball['vel'].y *= -1
            ball['pos'].y = h - ball['rad']
        case Wall.TOP:
            ball['vel'].y *= -1
            ball['pos'].y = ball['rad']
        case _:
            return None

    return None


def vec_scalar(vec: Vec) -> float:
    return math.sqrt(math.pow(vec.x, 2) + math.pow(vec.y, 2))


def ball_draw(window: pygame.surface.Surface, ball: Ball) -> None:
    pygame.draw.circle(window,
                       C_BLACK,
                       (ball['pos'].x, ball['pos'].y),
                       ball['rad'])
    return None


def rect_draw(window: pygame.surface.Surface, rect: Rectangle) -> None:
    pygame.draw.rect(window,
                     C_BLACK,
                     (int(rect['pos'].x), int(rect['pos'].y), rect['width'], rect['height'])
                     )
    return None


def ball_update_pos(ball: Ball, dt: float) -> None:
    ball['pos'].x += ball['vel'].x * dt
    ball['pos'].y -= ball['vel'].y * dt


def rect_update_pos(rect: Rectangle, dt: float) -> None:
    rect['pos'].x += rect['vel'].x * dt
    friction = 50
    if abs(rect['vel'].x) <= friction * dt:
        rect['vel'].x = 0

    if rect['vel'].x > 0:
        rect['vel'].x -= friction * dt
    elif rect['vel'].x < 0:
        rect['vel'].x += friction * dt


def draw_trans_bg(window: pygame.surface.Surface, w: int, h: int) -> None:
    pygame.draw.rect(window, C_BLUE, (0, 0, w, h // 5))
    pygame.draw.rect(window, C_PINK, (0, h // 5, w, h // 5))
    pygame.draw.rect(window, C_WHITE, (0, 2 * (h // 5), w, h // 5))
    pygame.draw.rect(window, C_PINK, (0, 3 * (h // 5), w, h // 5))
    pygame.draw.rect(window, C_BLUE, (0, 4 * (h // 5), w, h // 5))


def main() -> None:
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Firstgame')

    w_width = 750
    w_height = 500
    window = pygame.display.set_mode((w_width, w_height))

    ball = Ball(rad=40, pos=Pos(50, 300), vel=Vec(150, 120))
    rect = Rectangle(pos=Pos(50, w_height - 10), width=w_width // 8, height=12, vel=Vec(100, 100))

    running = True

    draw_trans_bg(window, w_width, w_height)
    clock = pygame.time.Clock()
    frames = 60
    dt = 1 / frames

    score = 0
    font = pygame.font.SysFont('freesans', 24)
    text = font.render(f'score: {score}', True, (0, 0, 0))

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.VIDEORESIZE | pygame.FULLSCREEN:
                    w_width, w_height = window.get_size()
                    rect['pos'].y = w_height - 10
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_LEFT:
                            rect['vel'].x -= 70
                        case pygame.K_RIGHT:
                            rect['vel'].x += 70
                        case pygame.K_DOWN:
                            print(event)
                        case pygame.K_UP:
                            print(event)

        rt = ball_check_wall_collition(ball, w_width, w_height)

        match ball_check_lose_condition(ball, rect, w_height):
            case BallState.LOSE:
                ball = Ball(rad=40, pos=Pos(50, 300), vel=Vec(150, 120))
                score = 0
                text = font.render(f'score: {score}', True, (0, 0, 0))
                continue
            case BallState.BOUNCE:
                ball['vel'].y *= -1
                score += 1
                text = font.render(f'score: {score}', True, (0, 0, 0))

        ball_handle_wall_collition(ball, rt, w_width, w_height)

        rect_update_pos(rect, dt)

        ball_update_pos(ball, dt)
        draw_trans_bg(window, w_width, w_height)
        ball_draw(window, ball)
        rect_draw(window, rect)
        window.blit(text, (0, 0))

        pygame.display.flip()
        clock.tick(frames)

    pygame.quit()
    return None


if __name__ == '__main__':
    main()
