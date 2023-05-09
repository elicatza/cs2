#!/usr/bin/env python

from __future__ import annotations
import pygame
from dataclasses import dataclass
from typing import TypeVar
from enum import Enum
import random


T = TypeVar('T')

ROWCOL = 10


class Color(Enum):
    BLUE = (85, 205, 252)
    PINK = (247, 168, 184)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


class BoardColor(Enum):
    SINOPIA = (214, 41, 0)
    ATOMIC_TANGERINE = (255, 155, 85)
    SUPER_PINK = (212, 97, 166)
    FLIRT = (165, 0, 98)


@dataclass
class Vec:
    x: int
    y: int


@dataclass
class Square:
    pos: Vec
    dim: Vec
    color: BoardColor
    link: None | int = None

    def draw(self, window: pygame.surface.Surface) -> None:
        pygame.draw.rect(window,
                         self.color.value, (self.pos.x, self.pos.y, self.dim.x, self.dim.y))
        return None


@dataclass
class Ladder:
    src: Vec
    dest: Vec
    color: Color

    def draw(self, window: pygame.surface.Surface, sidelen: int) -> None:

        pygame.draw.line(window,
                         self.color.value,
                         (self.src.x + sidelen // 4, self.src.y - sidelen // 3 + sidelen),
                         (self.dest.x + sidelen // 4, self.dest.y - sidelen // 3 + sidelen),
                         width=6)
        pygame.draw.line(window,
                         self.color.value,
                         (self.src.x + sidelen // 1.5, self.src.y - sidelen // 3 + sidelen),
                         (self.dest.x + sidelen // 1.5, self.dest.y - sidelen // 3 + sidelen),
                         width=6)


@dataclass
class Board:
    board: list[list[Square]]
    ladders: list[Ladder]
    sidelen: int
    row: int
    col: int

    @staticmethod
    def construct(w_width: int, w_height: int) -> Board:
        # TODO make an colormap
        offx = 0
        offy = 0
        if w_width > w_height:
            offx = (w_width - w_height) // 2
            w_width = w_height

        if w_height > w_width:
            offy = (w_height - w_width) // 2
            w_height = w_width

        # Dont need width and height since they are equal
        rt: list[list[Square]] = []

        sidelen = w_width // ROWCOL
        for column in range(ROWCOL):
            innerlist: list[Square] = []
            for row in range(ROWCOL):
                innerlist.append(Square(
                    Vec(offx + row * sidelen, offy + column * sidelen),
                    Vec(sidelen, sidelen),
                    random.choice(list(BoardColor))))
            if column % 2 == 0:
                innerlist.reverse()
            rt.append(innerlist)

        rt.reverse()

        random_nums = iter(random.sample(range(0, (ROWCOL ** 2) - 1), 12))
        ladders: list[Ladder] = []
        for i in random_nums:
            target = next(random_nums)
            rt[i // ROWCOL][i % ROWCOL].link = target
            color = Color.PINK
            if i > target:
                color = Color.BLUE
            ladders.append(Ladder(
                rt[i // ROWCOL][i % ROWCOL].pos,
                rt[target // ROWCOL][target % ROWCOL].pos,
                color))

        return Board(rt, ladders, sidelen, ROWCOL, ROWCOL)

    def draw(self, window: pygame.surface.Surface, font: pygame.font.Font) -> None:
        for i, column in enumerate(self.board):
            for j, square in enumerate(column):
                square.draw(window)

                img = font.render(f'{i * 10 + j + 1}', True, Color.WHITE.value)
                window.blit(img, (square.pos.x, square.pos.y))

        for ladder in self.ladders:
            ladder.draw(window, self.sidelen)


class Player:

    def __init__(self, color: Color, board: Board, rad: int) -> None:
        self.color = color
        self.position = 0
        center_x = board.board[0][0].pos.x + board.board[0][0].dim.x // 2
        center_y = board.board[0][0].pos.y + board.board[0][0].dim.y // 2
        self.pos = Vec(center_x, center_y)
        self.rad = rad

    # 24 mai
    @staticmethod
    def throw_dice(min: int, max: int) -> int:
        '''
        Parameters
        ----------
        min: int
            Inclusive
        max: int
            Inclusive
        '''
        return random.randint(min, max)

    def move(self, board: Board, positions: int) -> None:
        self.position += positions
        col = self.position // board.row
        row = self.position % board.row

        # Move to link if landig on link
        link = board.board[col][row].link
        if link is not None:
            col = link // board.row
            row = link % board.row
            self.position = link

        self.pos.x = board.board[col][row].pos.x + board.board[col][row].dim.x // 2
        self.pos.y = board.board[col][row].pos.y + board.board[col][row].dim.y // 2
        return None

    def draw(self, window: pygame.surface.Surface) -> None:
        pygame.draw.circle(window, self.color.value, (self.pos.x, self.pos.y), radius=self.rad)
        return None


def draw_trans_bg(window: pygame.surface.Surface, w: int, h: int) -> None:
    pygame.draw.rect(window, Color.BLUE.value, (0, 0, w, h // 5))
    pygame.draw.rect(window, Color.PINK.value, (0, h // 5, w, h // 5))
    pygame.draw.rect(window, Color.WHITE.value, (0, 2 * (h // 5), w, h // 5))
    pygame.draw.rect(window, Color.PINK.value, (0, 3 * (h // 5), w, h // 5))
    pygame.draw.rect(window, Color.BLUE.value, (0, 4 * (h // 5), w, h // 5))


def main() -> None:

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Firstgame')

    font = pygame.font.SysFont('freesans', 24)
    big_font = pygame.font.SysFont('freesans', 256)

    w_width = 800
    w_height = 800
    window = pygame.display.set_mode((w_width, w_height))

    clock = pygame.time.Clock()
    frames = 60
    # dt = 1 / frames

    draw_trans_bg(window, w_width, w_height)
    board = Board.construct(w_width, w_height)
    board.draw(window, font)

    p1 = Player(Color.WHITE, board, 20)
    p2 = Player(Color.BLACK, board, 20)
    p1.draw(window)
    p2.draw(window)
    turn = 0

    running = True
    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.VIDEORESIZE | pygame.FULLSCREEN:
                    w_width, w_height = window.get_size()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_UP | pygame.K_SPACE | pygame.K_k:
                            board.draw(window, font)

                # img = font.render(f'{i * 10 + j + 1}', True, Color.WHITE.value)
                # window.blit(img, (square.pos.x, square.pos.y))
                            die = random.randint(1, 6)
                            if turn % 2:
                                p1.move(board, die)
                                text = big_font.render(f'{die}', True, p1.color.value)
                            else:
                                p2.move(board, die)
                                text = big_font.render(f'{die}', True, p2.color.value)

                            p2.draw(window)
                            p1.draw(window)
                            text_rect = text.get_rect(center=(w_width // 2, w_height // 2))
                            window.blit(text, text_rect)
                            turn += 1

        pygame.display.flip()
        clock.tick(frames)

    pygame.quit()
    return None


if __name__ == '__main__':
    main()
