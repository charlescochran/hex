#! /usr/bin/env python3

import pygame as pg
import math
import matplotlib.path
import numpy as np
import time


class Hex():

    def __init__(self):
        self.board_size = 11
        self.colors = {'bg': (30, 30, 30),
                       'main': (201, 173, 200),
                       'p1': (255, 80, 80),
                       'p2': (54, 92, 255)}
        self.screen_width = 1620
        pg.init()
        self._init_game()
        self._init_board()
        self._init_screen()
        self._play()

    def _init_game(self):
        self.player = 1
        self.prev_moves = []

    def _init_board(self):
        self.board = [[0] * self.board_size for _ in range(self.board_size)]

    def _init_screen(self):
        # Choose an aspect ratio for the screen (change with caution)
        self.screen_size = (self.screen_width, self.screen_width / 1.5)
        # Initialize the window to be half as wide as the physical display
        init_display_width = pg.display.Info().current_w / 2
        init_display_height = init_display_width * self.screen_size[1] / self.screen_size[0]
        self.display = pg.display.set_mode((init_display_width, init_display_height), pg.RESIZABLE)
        # Create the virtual screen surface on which to draw everything
        self.screen = pg.Surface((self.screen_size))

        # Draw background
        self.screen.fill(self.colors['bg'])

        # Draw borders

        # Arbitrarily choose a horizontal position for the top left corner of the border
        top_left = []
        top_left.append(int(self.screen_size[0] / 15))
        # Then, do some math to find the corresponding vertical position for
        # the top left corner which, when mirrored to the bottom right corner,
        # will result in a border with an appropriate aspect ratio
        top_left.append(int((((2 / 3) - math.tan(math.pi / 6)) * self.screen_size[0] / 2)
                            + (math.tan(math.pi / 6) * top_left[0])))
        # Find the other three corners' coordinates based on the top left corner's coordinates
        top_right = (int((2 * self.screen_size[0] - top_left[0]) / 3), top_left[1])
        bottom_right = (self.screen_size[0] - top_left[0],
                        self.screen_size[1] - top_left[1])
        bottom_left = (self.screen_size[0] - top_right[0],
                       self.screen_size[1] - top_right[1])
        # Actually draw the border
        pg.draw.line(self.screen, self.colors['p1'], top_left, top_right, width=10)
        pg.draw.line(self.screen, self.colors['p2'], top_right, bottom_right, width=10)
        pg.draw.line(self.screen, self.colors['p1'], bottom_right, bottom_left, width=10)
        pg.draw.line(self.screen, self.colors['p2'], bottom_left, top_left, width=10)

        # Draw board

        # The number of hex radii in between the top left hex's center
        # and the top left edge of the border.
        margin = 3
        board_width = bottom_right[0] - top_left[0]
        # This complicated calculation specifies the radius of each
        # hexagon, in pixels. It ensures the board always fits neatly
        # within the border, no matter what board_size is used.
        self.hex_radius = board_width / (((3 * self.board_size) + margin) * math.cos(math.pi / 6))
        self.line_width = int(self.screen_size[0] / 180)
        x_shift_offset = self.hex_radius * math.cos(math.pi / 6)
        x_shift_width = 2 * x_shift_offset
        y_shift_height = self.hex_radius * (1 + math.sin(math.pi / 6))
        hex_origin = (top_left[0] + self.hex_radius * margin * math.cos(math.pi / 6),
                      top_left[1] + self.hex_radius * margin * math.sin(math.pi / 6))
        self.hex_positions = []
        for j in range(self.board_size):
            row = []
            for i in range(self.board_size):
                x_pos = hex_origin[0] + i * x_shift_width + j * x_shift_offset
                y_pos = hex_origin[1] + j * y_shift_height
                row.append((x_pos, y_pos))
            self.hex_positions.append(row)
        for row in self.hex_positions:
            for pos in row:
                self._draw_hexagon(pos, self.colors['main'], False)

        # Draw logo
        small_font = pg.font.SysFont('Ubuntu Mono', int(self.hex_radius * 1.5))
        large_font = pg.font.SysFont('Ubuntu Mono', int(self.hex_radius * 5), bold=True)
        top_right_hex = self.hex_positions[0][self.board_size - 1]
        logo_origin = (top_right_hex[0] + int(self.hex_radius * 3.6),
                       top_right_hex[1] - int(self.hex_radius * 2.5))
        self.screen.blit(small_font.render('the game of', True, self.colors['main']), logo_origin)
        logo_origin_2 = (logo_origin[0] + int(self.hex_radius * 0.9),
                         logo_origin[1] + int(self.hex_radius * 1))
        self.screen.blit(large_font.render('hex', True, self.colors['main']), logo_origin_2)

        # Create buttons
        # def __init__(self, screen, pos, font_size, text, text_color, button_color, click_cb):
        bottom_left_hex = self.hex_positions[self.board_size - 1][0]
        button_origin = (bottom_left_hex[0] - int(self.hex_radius * 10),
                         bottom_left_hex[1] - int(self.hex_radius * 4))
        self.undo_button = Button(self.screen, button_origin, int(self.hex_radius * 1.2), 'undo',
                                  self.colors['bg'], self.colors['main'], self.undo_button_cb,
                                  False)
        button_origin_2 = (button_origin[0], button_origin[1] + int(self.hex_radius * 2.5))
        self.swap_button = Button(self.screen, button_origin_2, int(self.hex_radius * 1.2), 'swap',
                                  self.colors['bg'], self.colors['main'], self.swap_button_cb,
                                  False)
        self.buttons = [self.undo_button, self.swap_button]

    def undo_button_cb(self):
        self._fill_hexagon(self.prev_moves[-1], 0)
        self.prev_moves.pop()
        # If we are undoing a swap
        if len(self.prev_moves) == 0 and self.player == 1:
            self._move(self.swapped_index)
            self.swapped_index = "nope"
        else:
            self.player = (self.player % 2) + 1
        self._update_buttons()

    def swap_button_cb(self):
        self.swapped_index = self.prev_moves[-1]
        self.undo_button_cb()
        self.player = 2
        self._move((self.swapped_index[1], self.swapped_index[0]))

    def _draw_hexagon(self, pos, color, filled):
        hex_vertices = self._calc_hex_vertices(pos)
        pg.draw.polygon(self.screen, color, hex_vertices, width=0 if filled else self.line_width)

    def _calc_hex_vertices(self, hex_pos):
        hex_vertices = []
        for i in range(6):
            angle = ((i * 2 - 1) / 6) * math.pi
            hex_vertices.append((hex_pos[0] + self.hex_radius * math.cos(angle),
                                 hex_pos[1] + self.hex_radius * math.sin(angle)))
        return hex_vertices

    def _play(self):
        self._update_display()
        self.running = True
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.VIDEORESIZE:
                    self._update_display()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse_presses = pg.mouse.get_pressed()
                    if mouse_presses[0]:
                        click_pos = pg.mouse.get_pos()
                        # Convert the click position from display coordinates
                        # to virtual screen coordinates
                        screen_x = (click_pos[0] - self.scaled_origin[0]) / self.scale_factor
                        screen_y = (click_pos[1] - self.scaled_origin[1]) / self.scale_factor
                        self._handle_click((screen_x, screen_y))
                        self._update_display()
            time.sleep(1/100)

    def _update_display(self):
        self.display_size = self.display.get_rect().size
        self.scale_factor = min(self.display_size[0] / self.screen_size[0],
                                self.display_size[1] / self.screen_size[1])
        self.scaled_size = (self.screen_size[0] * self.scale_factor,
                            self.screen_size[1] * self.scale_factor)
        self.scaled_origin = ((self.display_size[0] - self.scaled_size[0]) / 2,
                              (self.display_size[1] - self.scaled_size[1]) / 2)
        # Copy the virtual screen surface onto the actual display surface,
        # scaling and translating it appropriately
        self.display.blit(pg.transform.scale(self.screen, self.scaled_size), self.scaled_origin)
        pg.display.flip()

    def _fill_hexagon(self, index, player):
        self.board[index[1]][index[0]] = player
        pos = self.hex_positions[index[1]][index[0]]
        if player == 0:
            fill_color = self.colors['bg']
        else:
            fill_color = self.colors['p' + str(player)]
        # Fill hexagon
        self._draw_hexagon(pos, fill_color, True)
        # Redraw hexagon edges
        self._draw_hexagon(pos, self.colors['main'], False)

    def _handle_click(self, click_screen_pos):
        for button in self.buttons:
            if button.rect.collidepoint(click_screen_pos):
                button.handle_click()
        nearest_hex_index = ()
        min_dist = math.inf
        for j in range(len(self.hex_positions)):
            for i in range(len(self.hex_positions[j])):
                hex_pos = self.hex_positions[j][i]
                dist = math.dist(hex_pos, click_screen_pos)
                if dist < min_dist:
                    min_dist = dist
                    nearest_hex_index = (i, j)
        hex_vertices = self._calc_hex_vertices(
            self.hex_positions[nearest_hex_index[1]][nearest_hex_index[0]])
        hex_path = matplotlib.path.Path(np.array([vertex for vertex in hex_vertices]))
        if hex_path.contains_point(click_screen_pos):
            if self.board[nearest_hex_index[1]][nearest_hex_index[0]] == 0:
                self._move(nearest_hex_index)

    def _move(self, index):
        self.prev_moves.append(index)
        self._fill_hexagon(index, self.player)
        walls = [False, False]
        self._check_for_walls(walls, index, [])
        # If the current player's hex chain is touching both of his walls, end the game
        if walls[0] and walls[1]:
            print(f'Game over! Player {self.player} wins!')
            self.running = False
        # Toggle whose turn it is
        self.player = (self.player % 2) + 1
        self._update_buttons()

    def _update_buttons(self):
        if len(self.prev_moves) == 1:
            self.undo_button.enabled = True
            self.undo_button.redraw()
            if self.player == 2:
                self.swap_button.enabled = True
                self.swap_button.redraw()
        elif self.swap_button.enabled:
            self.swap_button.enabled = False
            self.swap_button.redraw()
        if len(self.prev_moves) < 1:
            self.undo_button.enabled = not self.undo_button.enabled
            self.undo_button.redraw()

    def _check_for_walls(self, walls, index, blacklist):
        # If current hex has already by checked or is not occupied by the player, return
        if index in blacklist or not self.board[index[1]][index[0]] == self.player:
            return
        # If the current hex is touching the player's first wall, set walls[0] to True
        if index[self.player % 2] == 0:
            walls[0] = True
        # If the current hex is touching the player's second wall, set walls[1] to True
        elif index[self.player % 2] == self.board_size - 1:
            walls[1] = True
        # Recursively call _check_for_walls() for all neighbor hexs, adding this one to the
        # blacklist to prevent it from being called checked again
        blacklist.append(index)
        for neighbor_index in self._get_neighbor_indices(index):
            self._check_for_walls(walls, neighbor_index, blacklist)

    def _get_neighbor_indices(self, index):
        # When given an hex's index, return the indices of all of its
        # neighbors. A corner hex has 2 neighbors, an edge hex has 4 neighbors,
        # and all other hexs have 6 neighbors.
        neighbor_indices = []
        for j in range(index[1] - 1, index[1] + 2):
            for i in range(index[0] - 1, index[0] + 2):
                if i in range(self.board_size) and j in range(self.board_size):
                    if not (i == index[0] and j == index[1]):
                        if abs(sum(index) - sum((i, j))) <= 1:
                            neighbor_indices.append((i, j))
        return neighbor_indices


class Button():

    def __init__(self, screen, pos, font_size, text, text_color, button_color, click_cb, enabled):
        self._screen = screen
        self._pos = pos
        self._font_size = font_size
        self._text = text
        self._text_color = text_color
        self._button_color = button_color
        self._click_cb = click_cb
        self.enabled = enabled
        self.redraw()

    def handle_click(self):
        if self.enabled:
            self._click_cb()

    def redraw(self):
        font = pg.font.SysFont('Ubuntu Mono', self._font_size)
        colors = (self._text_color, self._button_color) if self.enabled else (self._button_color, self._text_color)
        text_render = font.render(self._text, True, colors[0])
        _, _, w, h = text_render.get_rect()
        x, y = self._pos
        margin = self._font_size / 4
        self.rect = pg.draw.rect(self._screen, colors[1], (x - margin, y - margin,
                                                          w + 2 * margin, h + 2 * margin))
        self._screen.blit(text_render, (x, y))


if __name__=='__main__':
    hex = Hex()
