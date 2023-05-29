#!/usr/bin/env python

from __future__ import annotations

import pygame
from collections import deque
import math
import sys
import os
import time


C_BLUE = (85, 205, 252)
C_PINK = (247, 168, 184)
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)

BOTTOM_H = 1 / 15
TOP_H = 1 - BOTTOM_H


def draw_bg(window: pygame.surface.Surface, w: int, h: int) -> None:
    pygame.draw.rect(window, C_BLUE, (0, 0, w, math.ceil(h * TOP_H)))
    pygame.draw.rect(window, C_WHITE, (0, math.ceil(h * TOP_H), w, math.ceil(h * BOTTOM_H)))
    pygame.draw.rect(window, C_PINK, (0, math.ceil(h * TOP_H), w, math.ceil(h * (BOTTOM_H ** 2))))


class Carousel:

    def __init__(self, images: deque[Image], texts: deque[Text]):
        self.images = images
        self.texts = texts
        self.curr_id = 0

    def next(self) -> bool:
        if self.curr_id + 1 >= len(self.images):
            return False
        self.curr_id += 1
        return True

    def prev(self) -> bool:
        if self.curr_id <= 0:
            return False
        self.curr_id -= 1
        return True

    def render_imgs(self, new_h: int) -> None:
        for image in self.images:
            image.render(new_h)

    def center_imgs(self, w: int, h: int) -> None:
        for image in self.images:
            image.center(w, h)

    def position_texts(self, x: int, y: int) -> None:
        for text in self.texts:
            text.position(x, y)

    def render_texts(self, size: int) -> None:
        for text in self.texts:
            text.render(size)

    def draw(self, window: pygame.surface.Surface) -> None:
        self.images[self.curr_id].draw(window)
        self.texts[self.curr_id].draw(window)
        return None


class Text:

    def __init__(self, text: str, font: pygame.font.Font, color: pygame.color.Color):
        self.text = font.render(text, True, color)
        self.plain_text = text
        self.color = color
        self.font = font
        self.posx = 0
        self.posy = 0

    def render(self, size: int) -> None:
        self.font = pygame.font.SysFont('freesans', size)
        self.text = self.font.render(self.plain_text, True, self.color)
        return None

    def position(self, x: int, y: int) -> None:
        self.posx = x
        self.posy = y

    def draw(self, window: pygame.surface.Surface) -> None:
        window.blit(self.text, (self.posx, self.posy))
        return None


class Image:

    def __init__(self, img: pygame.surface.Surface, desc: str):
        self.img = img
        self.img_resize = img
        self.width, self.height = img.get_size()
        self.offx = 0
        self.offy = 0

    def render(self, new_h: int) -> None:
        ratio = self.width / self.height
        new_w = math.ceil(new_h * ratio)
        self.img_resize = pygame.transform.scale(self.img, (new_w, new_h))
        self.width, self.height = self.img_resize.get_size()

    def center(self, w: int, h: int) -> None:
        self.offx = (w - self.width) // 2
        self.offy = (h - self.height) // 2

    def draw(self, window: pygame.surface.Surface) -> None:
        window.blit(self.img_resize, (self.offx, self.offy))
        return None


def parse_args() -> list[str]:
    files = sys.argv[1::]
    if len(files) == 0:
        for file in os.listdir("./assets"):
            files.append(os.path.join("./assets", file))
        print("Default: Showing all files in ./assets")
        print("You can select files to show by entering them as args")
        print("$ python main.py file.png another.webp third.jpg")
    return files


def main() -> None:
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('spiv')

    w_width = 800
    w_height = 500
    window = pygame.display.set_mode((w_width, w_height))

    clock = pygame.time.Clock()
    frames = 60

    font = pygame.font.SysFont('consolas', math.ceil(w_height * BOTTOM_H))

    imgs: deque[Image] = deque()
    texts: deque[Text] = deque()
    files = parse_args()
    for file in files:
        img = Image(pygame.image.load(file), file)
        img.render(math.ceil(w_height * TOP_H - w_height // 8))
        img.center(w_width, math.ceil(w_height * TOP_H))
        imgs.append(img)

        f_mod_time = time.strptime(time.ctime(os.path.getmtime(file)))
        text = Text(file + ": " + time.strftime("%Y-%m-%d", f_mod_time),
                    font,
                    pygame.color.Color((0, 0, 0)))
        text.position(0, math.ceil(w_height * TOP_H))
        text.render(math.ceil(w_height * BOTTOM_H))
        texts.append(text)

    carousel = Carousel(imgs, texts)

    running = True
    while running:
        for event in pygame.event.get():
            match event.type:

                case pygame.QUIT:
                    running = False

                case pygame.VIDEORESIZE | pygame.FULLSCREEN:
                    w_width, w_height = window.get_size()
                    carousel.render_imgs(math.ceil(w_height * TOP_H - w_height // 8))
                    carousel.center_imgs(w_width, math.ceil(w_height * TOP_H))
                    carousel.position_texts(0, math.ceil(w_height * TOP_H))
                    carousel.render_texts(math.ceil(w_height * BOTTOM_H))

                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_LEFT:
                            carousel.prev()
                        case pygame.K_RIGHT:
                            carousel.next()

            # Does not draw unless event update
            draw_bg(window, w_width, w_height)
            carousel.draw(window)
            pygame.display.flip()

        clock.tick(frames)

    pygame.quit()
    return None


if __name__ == '__main__':
    main()
