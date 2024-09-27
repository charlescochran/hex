#!/usr/bin/python3

# Random imports required to get pygbag to work
import PIL, numpy, cycler, kiwisolver, matplotlib, dateutil, six

import asyncio
import time

import pygame as pg

import game, display


class Main():

    def __init__(self):
        pg.init()
        self._display = display.Display()
        self._game = game.Game(self._display, 11, game.Game.Mode.HH)

    async def play(self):
        self.running = True
        self._display.update()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.VIDEORESIZE:
                    self._display.update()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if pg.mouse.get_pressed()[0]:
                        self._display.handle_click(pg.mouse.get_pos())
                        self._display.update()
            await asyncio.sleep(0)
            time.sleep(1/100)


if __name__ == '__main__':
    asyncio.run(Main().play())
