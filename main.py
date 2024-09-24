#!/usr/bin/python3

# Random imports required to get pygbag to work
import PIL, numpy, cycler, kiwisolver, matplotlib, dateutil, six

import asyncio

import game


if __name__ == '__main__':
    asyncio.run(game.Game().play())
