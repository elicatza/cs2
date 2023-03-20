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


@dataclass
class Vec:
    x: float
    y: float


@dataclass
class Pos:
    x: float
    y: float


class Ball(TypedDict):
    rad: int
    pos: Pos
    acc: Vec
    vel: Vec


def ball_check_wall_collition(ball: Ball, w: int, h: int) -> Wall:
    if ball['pos'].x < ball['rad']:
        return Wall.LEFT

    if ball['pos'].x > w - ball['rad']:
        return Wall.RIGHT

    if ball['pos'].y < ball['rad']:
        return Wall.TOP

    if ball['pos'].y > h - ball['rad']:
        return Wall.BOTTOM

    return Wall.NONE


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


def ball_handle_ball_collition(a: Ball, b: Ball) -> None:
    # https://en.wikipedia.org/wiki/Elastic_collision#Two-Dimensional_Collision_With_Two_Moving_Objects
    v1 = vec_scalar(a['vel'])
    v2 = vec_scalar(b['vel'])
    # TODO: actual mass calc
    m1 = math.pi * (a['rad'] ** 2)
    m2 = math.pi * (b['rad'] ** 2)
    try:
        theta1 = 1 / math.tan(a['vel'].y / a['vel'].x)
    except ZeroDivisionError:
        theta1 = 0
    try:
        theta2 = 1 / math.tan(b['vel'].y / b['vel'].x)
    except ZeroDivisionError:
        theta2 = 0
    # TODO: calculate phi (contact angle)
    diff_vec = Vec(a['pos'].x - b['pos'].x, a['pos'].y - b['pos'].y)
    try:
        phi = 1 / math.tan(diff_vec.y / diff_vec.x)
    except ZeroDivisionError:
        phi = 0
    print(theta1, theta2, phi)

    a['vel'].x = ((v1 * math.cos(theta1 - phi) * (m1 - m2) + 2 * m2 * v2 * math.cos(theta2 - phi)) / (m1 + m2)) * math.cos(phi) + v1 * math.sin(theta1 - phi) * math.cos(phi + math.pi / 2)
    a['vel'].y = ((v1 * math.cos(theta1 - phi) * (m1 - m2) + 2 * m2 * v2 * math.cos(theta2 - phi)) / (m1 + m2)) * math.sin(phi) + v1 * math.sin(theta1 - phi) * math.sin(phi + math.pi / 2)

    return None


def ball_check_ball_collition(a: Ball, b: Ball) -> bool:
    col_val = a['rad'] + b['rad']

    x = a['pos'].x - b['pos'].x
    y = a['pos'].y - b['pos'].y

    if x ** 2 + y ** 2 < col_val ** 2:
        return True

    return False


def ball_draw(window: pygame.surface.Surface, ball: Ball) -> None:
    pygame.draw.circle(window,
                       C_BLACK,
                       (ball['pos'].x, ball['pos'].y),
                       ball['rad'])
    return None


def ball_update_pos(ball: Ball, dt: float) -> None:
    ball['pos'].x += ball['vel'].x * dt
    ball['pos'].y -= ball['vel'].y * dt


def ball_update_vel(ball: Ball, dt: float) -> None:
    ball['vel'].x += ball['acc'].x * dt
    ball['vel'].y += ball['acc'].y * dt


def draw_trans_bg(window: pygame.surface.Surface, w: int, h: int) -> None:
    pygame.draw.rect(window, C_BLUE, (0, 0, w, h // 5))
    pygame.draw.rect(window, C_PINK, (0, h // 5, w, h // 5))
    pygame.draw.rect(window, C_WHITE, (0, 2 * (h // 5), w, h // 5))
    pygame.draw.rect(window, C_PINK, (0, 3 * (h // 5), w, h // 5))
    pygame.draw.rect(window, C_BLUE, (0, 4 * (h // 5), w, h // 5))


def main() -> None:
    pygame.init()
    pygame.display.set_caption('Firstgame')

    w_width = 750
    w_height = 500
    window = pygame.display.set_mode((w_width, w_height))

    balls = [
            Ball(
                rad=70,
                pos=Pos(50, 300),
                vel=Vec(100, 100),
                acc=Vec(0, -9.81),
                ),
            Ball(
                rad=70,
                pos=Pos(100, -100),
                vel=Vec(-70, 100),
                acc=Vec(0, -9.81),
                )
            ]

    running = True

    draw_trans_bg(window, w_width, w_height)
    clock = pygame.time.Clock()
    frames = 55
    dt = 1 / frames

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.VIDEORESIZE | pygame.FULLSCREEN:
                    w_width, w_height = window.get_size()

        draw_trans_bg(window, w_width, w_height)
        for i, ball in enumerate(balls):
            rt = ball_check_wall_collition(ball, w_width, w_height)
            ball_handle_wall_collition(ball, rt, w_width, w_height)
            for j, iball in enumerate(balls):
                if j != i:
                    is_col = ball_check_ball_collition(ball, iball)
                    if is_col:
                        ball_handle_ball_collition(ball, iball)

            # ball_update_vel(ball, dt)
            ball_update_pos(ball, dt)
            ball_draw(window, ball)
        pygame.display.flip()
        clock.tick(frames)

    return None


if __name__ == '__main__':
    main()
