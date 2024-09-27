#!/usr/bin/python3

# Random imports required to get pygbag to work
import PIL, numpy, cycler, kiwisolver, matplotlib, dateutil, six

import asyncio
import random
import time

import pygame as pg

import game, display, menu


class Main():

    def __init__(self):
        pg.init()
        self._display = display.Display()

    def start_menu(self):
        self._display.reset()
        self._menu = menu.Menu(self._display, self.start_game)

    def start_game(self, board_size, mode):
        if mode == 4:  # "1P (random)" mode
            mode = random.randint(2, 3)
        self._display.reset()
        self._game = game.Game(self._display, board_size, mode, self.game_over)

    def game_over(self, winner):
        print(f'Game over! Player {winner} wins!')
        self._display.reset(clear=False)

    async def loop(self):
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
    main = Main()
    main.start_menu()
    asyncio.run(main.loop())
