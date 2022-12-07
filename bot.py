import random


class Bot():

    def __init__(self, board_size, move_cb, swap_cb):
        self.board_size = board_size
        self.move_cb = move_cb
        self.swap_cb = swap_cb

    def move(self, board):
        # Loop until a legal move is found
        while True:
            # Decide what move to make (for now: random)
            index = (random.randrange(0, self.board_size), random.randrange(0, self.board_size))
            # If move is legal, make it and end the loop
            if board[index[1]][index[0]] == 0:
                self.move_cb(index, bot_should_respond=False)
                break

    def can_swap(self, board):
        # For now: choose whether or not to swap randomly
        if random.choice([True, False]):
            self.swap_cb()
        # If we don't swap, move instead
        else:
            self.move(board)
