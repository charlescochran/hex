from enum import Enum

from bot import Bot


class Game():

    # Player Modes:
    #   HH - Both players are human; none are bots.
    #   HB - The first player is human; the second is a bot.
    #   BH - The first player is a bot; the second is human.
    Mode = Enum('Mode', ['HH', 'HB', 'BH'])

    def __init__(self, display, board_size, mode):
        self._init_game(mode)
        self._init_board(board_size)
        self._init_display(display)
        self._init_bot()

    def _init_game(self, mode):
        self.mode = mode
        self.player = 1
        self.prev_moves = []

    def _init_board(self, board_size):
        self.board_size = board_size
        self.board = [[0] * board_size for _ in range(board_size)]

    def _init_display(self, display):
        self.display = display
        self.display.calc_positions(self.board_size)
        self.display.register_hex_click_cb(self.hex_click_cb)
        self.display.add_game_buttons((self.undo_enabled, self.undo),
                                      (self.swap_enabled, self.swap))
        self.display.draw_board(self.board_size)
        self.display.draw_border()
        self.display.draw_logo()
        self.display.draw_buttons()

    def _init_bot(self):
        self.bot = Bot(self.board_size, self.move, self.swap)
        # If the bot needs to go first, make it
        if self.mode is self.Mode.BH:
            self.bot.move(self.board)

    def undo_enabled(self):
        if len(self.prev_moves) > 1:
            return True
        if len(self.prev_moves) == 1 and self.mode is not self.Mode.BH:
            return True
        return False

    def swap_enabled(self):
        return len(self.prev_moves) == 1 and self.player == 2

    def hex_click_cb(self, index):
        if self.board[index[0]][index[1]] == 0:
            self.move(index, bot_should_respond=self.mode is not self.Mode.HH)

    def move(self, index, bot_should_respond=False, currently_swapping=False):
        self.prev_moves.append(index)
        self.board[index[0]][index[1]] = self.player
        self.display.draw_hex(index, self.player)
        walls = [False, False]
        self._check_for_walls(walls, index, [])
        # If the current player's hex chain is touching both of his walls, end
        # the game
        if walls[0] and walls[1]:
            print(f'Game over! Player {self.player} wins!')
            self.running = False
        # Toggle whose turn it is
        self.player = (self.player % 2) + 1
        # If the bot should respond (indicating that this is a human move and
        # the other player is a bot)...
        if bot_should_respond:
            # If this was the human's first move, give the bot the option of swapping
            if len(self.prev_moves) == 1 and not currently_swapping:
                self.bot.can_swap(self.board)
            # Otherwise, trigger the bot's response move
            else:
                self.bot.move(self.board)
        # Always update the buttons after a move
        self.display.draw_buttons()

    def undo(self, currently_swapping=False):
        # If one of the players is a bot, we want the undo button to undo both
        # the human player's last move and the bot's last move. However, if
        # this undo is part of a swap, only undo once.
        double_undo = self.mode is not self.Mode.HH and not currently_swapping
        # For each undo...
        for _ in range(2 if double_undo else 1):
            # Clear the last hexagon and remove its indices from the previous
            # moves list
            self.board[self.prev_moves[-1][0]][self.prev_moves[-1][1]] = 0
            self.display.draw_hex(self.prev_moves[-1], 0)
            self.prev_moves.pop()
            # If we are undoing a swap...
            if len(self.prev_moves) == 0 and self.player == 1:
                # Replace the first player's swapped piece. Note that if the
                # first player is a human and the second is a bot, the bot's
                # response will not be triggered, and the second undo will undo
                # the human's replaced move (allowing them to choose a
                # different starting move).
                self.move(self.swapped_index, bot_should_respond=False)
                self.swapped_index = None
            # Otherwise, if we are not currently swapping, toggle the player
            elif not currently_swapping:
                self.player = (self.player % 2) + 1
        # Always update the buttons after an undo
        self.display.draw_buttons()

    def swap(self):
        self.swapped_index = self.prev_moves[-1]
        # First, undo the first player's first move
        self.undo(currently_swapping=True)
        # Then, replace it with the second player's first move, mirroring the first player's
        self.move((self.swapped_index[1], self.swapped_index[0]),
                  bot_should_respond=self.mode is self.Mode.BH, currently_swapping=True)
        # Note: the buttons are updated by the move

    def _check_for_walls(self, walls, index, blacklist):
        # If current hex has already by checked or is not occupied by the player, return
        if index in blacklist or not self.board[index[0]][index[1]] == self.player:
            return
        # If the current hex is touching the player's first wall, set walls[0] to True
        if index[self.player - 1] == 0:
            walls[0] = True
        # If the current hex is touching the player's second wall, set walls[1] to True
        elif index[self.player - 1] == self.board_size - 1:
            walls[1] = True
        # Recursively call _check_for_walls() for all neighbor hexs, adding this one to the
        # blacklist to prevent it from being called checked again
        blacklist.append(index)
        for neighbor_index in self._get_neighbor_indices(index):
            self._check_for_walls(walls, neighbor_index, blacklist)

    def _get_neighbor_indices(self, index):
        # When given an hex's index, return the indices of all of its
        # neighbors. A corner hex has 2 or 3 neighbors, an edge hex has 4
        # neighbors, and all other hexes have 6 neighbors.
        neighbor_indices = []
        for j in range(index[1] - 1, index[1] + 2):
            for i in range(index[0] - 1, index[0] + 2):
                if not i in range(self.board_size) or not j in range(self.board_size):
                    continue
                if i == index[0] and j == index[1]:
                    continue
                if abs(sum(index) - sum((i, j))) > 1:
                    continue
                neighbor_indices.append((i, j))
        return neighbor_indices
