import Network
import Topology
import GameBoard
import random
from copy import deepcopy
import C4NN
import pickle

new_net = input("New network?(y/n)")
ai = None
if new_net == "y":
    ai = C4NN.C4NN()
else:
    ai_file = open("AIstoragefile", "rb")
    ai = pickle.load(ai_file)

ai.train_phase1(1000, 3)

#Play 1000 games
for i in range(1000):
    print("Net set " + str(i))
    board = GameBoard.GameBoard()
    opponent = deepcopy(ai)
    #play the game once for net starting, once for opponent starting
    for i in range(2):
        redPlayer = None
        blackPlayer = None
        if i == 0:
            redPlayer = ai
            blackPlayer = opponent
        if i == 1:
            redPlayer = opponent
            blackPlayer = ai
        # play the game until won or tied
        while not (board.won or board.tied):
            if board.whoseTurn() == 1:
                board.make_move(redPlayer.best_move(board))
            else:
                board.make_move(blackPlayer.best_move(board))
            for layer in board.board:
                print(layer)
            print()
            print()

        #here. find out who won. record this.
    #If the same player won both times, set that player as the new ai.
    #Otherwise, find some way to reconcile it. Perhaps throw out both games, or assign a random one to be the winner.
    #A tiebreaker likely wouldn't work, because the game would go exactly the way the first one did.


# board = GameBoard.GameBoard()
# win = False
# while not win:
#     i = int(input("Please make a move between 0 and 6\n"))
#     win = board.make_move(i)
#     for layer in board.board:
#         print(layer)

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


