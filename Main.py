import Network
import Topology
import GameBoard
import random

# Training part 1 - assign targets via some sort of equation.
# Possible equation: max # of my chips in a row / max # of opponent's chips in a row

# generate arbitrary number of game boards - let's say 100000. 0 is empty, 1 is red, 2 is black
game_boards = []
# while len(game_boards) < 100000:
#     board = GameBoard.GameBoard()

board = GameBoard.GameBoard()
win = False
while not win:
    i = int(input("Please make a move between 0 and 6\n"))
    win = board.make_move(i)
    for layer in board.board:
        print(layer)

# board.make_move(0)
# board.make_move(0)
# board.make_move(1)
# board.make_move(0)
# board.make_move(2)
# board.make_move(3)
# board.make_move(3)
# board.make_move(4)
# board.make_move(5)
# board.make_move(4)
# board.make_move(4)
# board.make_move(5)
# board.make_move(5)
# board.make_move(6)
# board.make_move(5)


