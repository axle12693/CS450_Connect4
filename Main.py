import Network
import Topology
import GameBoard
import random
from copy import deepcopy
import C4NN
import pickle
from termcolor import colored
import sys
import numpy as np

new_net = input("New network?(y/n)")
ai = None
if new_net == "y":
    ai = C4NN.C4NN()
else:
    ai_file = open("AIstoragefile", "rb")
    ai = pickle.load(ai_file)

#ai.train_phase1(1000, 500)

#Play 1000 games
for i in range(1000):
    print("Net set " + str(i))
    opponent = deepcopy(ai)
    opponent.mutate()
    wins = {"ai":0, "opponent":0}
    done_playing = False
    #play the game once for net starting, once for opponent starting
    play = 0
    while not done_playing:
        print("Playthough: " + str(play))
        board = None
        board = GameBoard.GameBoard()
        redPlayer = None
        blackPlayer = None
        if play % 2 == 0:
            redPlayer = deepcopy(ai)
            blackPlayer = deepcopy(opponent)
        else:
            redPlayer = deepcopy(opponent)
            blackPlayer = deepcopy(ai)
        play += 1
        # play the game until won or tied
        while not board.won and not board.tied:
            if 0 not in board.board[0]:
                board.print()
                raise Exception("You should never get this message!")
            if board.whoseTurn() == 1:
                print("Making red's move...")
                moves = np.ndarray.tolist(redPlayer.best_move(board))
                for index, move in enumerate(moves):
                    moves[index] = [index, move]
                moves = sorted(moves, key=lambda x: x[1])
                for i in range(7):
                    try:
                        board.make_move(moves[i][0])
                        break
                    except:
                        pass
            else:
                print("Making black's move...")
                moves = np.ndarray.tolist(blackPlayer.best_move(board))
                for index, move in enumerate(moves):
                    moves[index] = [index, move]
                moves = sorted(moves, key=lambda x: x[1])
                for i in range(7):
                    try:
                        board.make_move(moves[i][0])
                        break
                    except:
                        pass
            board.print()

        #here. find out who won. record this.
        if board.won:
            if play % 2 == 1:
                if board.won_by == 1:
                    wins["ai"] += 1
                else:
                    wins["opponent"] += 1
            else:
                if board.won_by == 1:
                    wins["opponent"] += 1
                else:
                    wins["ai"] += 1
            if wins["ai"] + wins["opponent"] >= 2:
                if wins["ai"] > wins["opponent"]:
                    done_playing = True
                    print(wins)
                    print("My opponent was sucky!")
                elif wins["opponent"] > wins["ai"]:
                    ai = deepcopy(opponent)
                    print(wins)
                    print("Found a slightly better AI!")
                    done_playing = True


ai_file = open("AIstoragefile", "wb")
pickle.dump(ai, ai_file)


print(colored("hello", "red"))

game = GameBoard.GameBoard()
while not (game.won or game.tied):
    if game.whoseTurn() == 1:
        game.print()
        move = int(input("What is your move?"))
        print("Making red's move...")
        game.make_move(move)
    else:
        print("Making black's move...")
        moves = np.ndarray.tolist(ai.best_move(game))
        for index, move in enumerate(moves):
            moves[index] = [index, move]
        moves = sorted(moves, key=lambda x: x[1])
        for i in range(7):
            try:
                game.make_move(moves[i][0])
                break
            except:
                pass






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


