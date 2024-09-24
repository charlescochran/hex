from typing import Callable
from dataclasses import dataclass
import math

import matplotlib.path

import pygame as pg


class Display():

    def __init__(self):
        self._buttons = []
        self.colors = {'bg': (30, 30, 30),
                       'main': (201, 173, 200),
                       'p1': (255, 80, 80),
                       'p2': (54, 92, 255)}
        # Virtual screen width (will be scaled to actual display size)
        screen_width = 1620
        # Choose an aspect ratio for the screen (change with caution)
        self.size = (screen_width, screen_width / 1.5)
        # Initialize the window to be half as wide as the physical display
        init_display_width = pg.display.Info().current_w / 2
        init_display_height = init_display_width * self.size[1] / self.size[0]
        self._display = pg.display.set_mode((init_display_width, init_display_height), pg.RESIZABLE)
        # Create the virtual screen surface on which to draw everything
        self.screen = pg.Surface((self.size))
        # Draw background
        self.screen.fill(self.colors['bg'])

    def calc_positions(self, board_size):
        self.border_pos = self._calc_border_position()
        self.hex_positions = self._calc_hex_positions(board_size)
        self.hex_vertices = self._calc_hex_vertices()

    def _calc_border_position(self):
        # Arbitrarily choose a horizontal position for the top left corner of the border
        top_left = [int(self.size[0] / 15)]
        # Then, do some math to find the corresponding vertical position for
        # the top left corner which, when mirrored to the bottom right corner,
        # will result in a border with an appropriate aspect ratio
        top_left.append(int((((2 / 3) - math.tan(math.pi / 6)) * self.size[0] / 2)
                            + (math.tan(math.pi / 6) * top_left[0])))
        # Find the other three corners' coordinates based on the top left corner's coordinates
        top_right = (int((2 * self.size[0] - top_left[0]) / 3), top_left[1])
        bottom_right = (self.size[0] - top_left[0], self.size[1] - top_left[1])
        bottom_left = (self.size[0] - top_right[0], self.size[1] - top_right[1])
        return top_left, top_right, bottom_right, bottom_left

    def _calc_hex_positions(self, board_size):
        # The number of hex radii in between the top left hex's center
        # and the top left edge of the border.
        margin = 3
        board_width = self.border_pos[2][0] - self.border_pos[0][0]
        # This complicated calculation specifies the radius of each
        # hexagon, in pixels. It ensures the board always fits neatly
        # within the border, no matter what board_size is used.
        self.hex_radius = board_width / (((3 * board_size) + margin) * math.cos(math.pi / 6))
        self.line_width = int(self.size[0] / 180)
        x_shift_offset = self.hex_radius * math.cos(math.pi / 6)
        x_shift_width = 2 * x_shift_offset
        y_shift_height = self.hex_radius * (1 + math.sin(math.pi / 6))
        hex_origin = (self.border_pos[0][0] + self.hex_radius * margin * math.cos(math.pi / 6),
                      self.border_pos[0][1] + self.hex_radius * margin * math.sin(math.pi / 6))
        hex_positions = []
        for j in range(board_size):
            row = []
            for i in range(board_size):
                x_pos = hex_origin[0] + i * x_shift_width + j * x_shift_offset
                y_pos = hex_origin[1] + j * y_shift_height
                row.append((x_pos, y_pos))
            hex_positions.append(row)
        return hex_positions

    def _calc_hex_vertices(self):
        hex_vertices = []
        for pos_row in self.hex_positions:
            row = []
            for pos in pos_row:
                vertices = []
                for i in range(6):
                    angle = ((i * 2 - 1) / 6) * math.pi
                    vertices.append((pos[0] + self.hex_radius * math.cos(angle),
                                     pos[1] + self.hex_radius * math.sin(angle)))
                row.append(vertices)
            hex_vertices.append(row)
        return hex_vertices

    def draw_hex(self, index, player):
        vertices = self.hex_vertices[index[0]][index[1]]
        if player == 0:
            # Filling with bg color allows for undos
            color = self.colors['bg']
        else:
            color = self.colors['p' + str(player)]
        # Fill hexagon
        pg.draw.polygon(self.screen, color, vertices, width=0)
        # Draw edges
        pg.draw.polygon(self.screen, self.colors['main'], vertices, width=self.line_width)

    def draw_board(self, board_size):
        for r in range(board_size):
            for c in range(board_size):
                self.draw_hex((r, c), 0)

    def draw_border(self):
        # Draw the border colors
        pg.draw.line(self.screen, self.colors['p1'], self.border_pos[0], self.border_pos[1],
                     width=self.line_width)
        pg.draw.line(self.screen, self.colors['p2'], self.border_pos[1], self.border_pos[2],
                     width=self.line_width)
        pg.draw.line(self.screen, self.colors['p1'], self.border_pos[2], self.border_pos[3],
                     width=self.line_width)
        pg.draw.line(self.screen, self.colors['p2'], self.border_pos[3], self.border_pos[0],
                     width=self.line_width)
        font = pg.font.SysFont('Ubuntu Mono', round(self.hex_radius))
        # Draw row letters down left side
        for r, row in enumerate(self.hex_positions):
            pos = (row[0][0] - 2.8 * self.hex_radius, row[0][1] - 0.5 * self.hex_radius)
            self.screen.blit(font.render(chr(r + 97), True, self.colors['main']), pos)
        # Draw col numbers across top
        for c, position in enumerate(self.hex_positions[0]):
            pos = (position[0] - 1.5 * self.hex_radius, position[1] - 2.8 * self.hex_radius)
            self.screen.blit(font.render(str(c + 1), True, self.colors['main']), pos)

    def draw_logo(self):
        # Create fonts, sized according to screen width
        small_font = pg.font.SysFont('Ubuntu Mono', int(self.size[0] / 24))
        large_font = pg.font.SysFont('Ubuntu Mono', int(self.size[0] * 5 / 36), bold=True)
        # Choose text origins based on screen size
        logo_origin = (self.size[0] * 93 / 128, self.size[1] / 8)
        logo_origin_2 = (self.size[0] * 3 / 4, self.size[1] / 6)
        # Draw the text
        self.screen.blit(small_font.render('the game of', True, self.colors['main']),
                          logo_origin)
        self.screen.blit(large_font.render('hex', True, self.colors['main']), logo_origin_2)

    def add_game_buttons(self, undo_data, swap_data):
        data = (('undo', *undo_data), ('swap', *swap_data))
        pos = [self.size[0] / 10, self.size[1] * 7 / 10]
        self._add_buttons(data, pos, vertical=True)

    def _add_buttons(self, data, pos, vertical):
        font = pg.font.SysFont('Ubuntu Mono', int(self.size[0] / 30))
        for (label, enabled_cb, click_cb) in data:
            button = Button(self, font, tuple(pos), label, enabled_cb, click_cb)
            self._buttons.append(button)
            if vertical:
                pos[1] += button.rect[3] + 0.75 * font.get_linesize()
            else:
                pos[0] += button.rect[2] + 0.75 * font.get_linesize()

    def draw_buttons(self):
        for button in self._buttons:
            button.draw()

    def register_hex_click_cb(self, hex_click_cb):
        self.hex_click_cb = hex_click_cb

    def handle_click(self, display_pos):
        # Convert the given display (e.g., click) position from display
        # coordinates to virtual screen coordinates
        screen_x = (display_pos[0] - self.scaled_origin[0]) / self.scale_factor
        screen_y = (display_pos[1] - self.scaled_origin[1]) / self.scale_factor
        for r, row in enumerate(self.hex_vertices):
            for c, vertices in enumerate(row):
                if matplotlib.path.Path(vertices).contains_point((screen_x, screen_y)):
                    self.hex_click_cb((r, c))
                    return
        for button in self._buttons:
            if button.rect.collidepoint((screen_x, screen_y)):
                button.handle_click()

    def update(self):
        display_size = self._display.get_rect().size
        self.scale_factor = min(display_size[0] / self.size[0],
                                display_size[1] / self.size[1])
        self.scaled_size = (self.size[0] * self.scale_factor,
                            self.size[1] * self.scale_factor)
        self.scaled_origin = ((display_size[0] - self.scaled_size[0]) / 2,
                              (display_size[1] - self.scaled_size[1]) / 2)
        # Blackout the display
        self._display.fill((0, 0, 0))
        # Copy the virtual screen surface onto the actual display surface,
        # scaling and translating it appropriately
        self._display.blit(pg.transform.smoothscale(self.screen, self.scaled_size),
                           self.scaled_origin)
        pg.display.flip()

@dataclass
class Button:
    _display: Display
    _font: pg.font.Font
    _pos: tuple[int, int]
    label: str
    enabled_cb: Callable
    click_cb: Callable

    def __post_init__(self):
        margin = self._font.get_linesize() / 4
        x, y = self._pos
        w, h = self._font.size(self.label)
        self.rect = pg.Rect(x - margin, y - margin, w + 2 * margin, h + 2 * margin)

    def handle_click(self):
        if self.enabled_cb():
            self.click_cb()

    def draw(self):
        if self.enabled_cb():
            text_color = self._display.colors['bg']
            bg_color = self._display.colors['main']
        else:
            text_color = self._display.colors['main']
            bg_color = self._display.colors['bg']
        text_render = self._font.render(self.label, True, text_color)
        pg.draw.rect(self._display.screen, bg_color, self.rect)
        self._display.screen.blit(text_render, self._pos)
