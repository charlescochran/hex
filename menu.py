class Menu():

    def __init__(self, display, start_game_cb):
        self._display = display
        self.size = None
        self.mode = None
        self._display.add_board_size_buttons(lambda size: self.size != size, self.size_cb)
        self._display.add_mode_buttons(lambda mode: self.mode != mode, self.mode_cb)
        self._display.add_start_button(
            lambda: self.size is not None and self.mode is not None,
            lambda: start_game_cb(self.size, self.mode)
        )
        self._display.draw_buttons()

    def size_cb(self, size):
        self.size = size
        self._display.draw_buttons()

    def mode_cb(self, mode):
        self.mode = mode
        self._display.draw_buttons()
