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
import math
import matplotlib.pyplot as plt


new_net = input("New network?(y/n)")
ai = None
if str.lower(new_net) == "y":
    ai = C4NN.C4NN()
else:
    ai_file = open("AIstoragefile_test", "rb")
    ai = pickle.load(ai_file)

# ai.train_phase1(num_boards=1000, num_epochs=10)
#
# ai_file = open("AIstoragefile_test", "wb")
# pickle.dump(ai, ai_file)
#
# upgrades = []
# upgrade_index = []
#
# # Play 1000 games
# for i in range(100):
#     print("Net set " + str(i))
#     opponent = deepcopy(ai)
#     opponent.mutate()
#     wins = {"ai":0, "opponent":0}
#     done_playing = False
#     #play the game once for net starting, once for opponent starting
#     play = 0
#     while not done_playing:
#         print("Playthough: " + str(play))
#         board = None
#         board = GameBoard.GameBoard()
#         redPlayer = None
#         blackPlayer = None
#         if play % 2 == 0:
#             redPlayer = deepcopy(ai)
#             blackPlayer = deepcopy(opponent)
#         else:
#             redPlayer = deepcopy(opponent)
#             blackPlayer = deepcopy(ai)
#         play += 1
#         if play > 10:
#             break
#         # play the game until won or tied
#         while not board.won and not board.tied:
#             if 0 not in board.board[0]:
#                 board.print()
#                 raise Exception("You should never get this message!")
#             if board.whoseTurn() == 1:
#                 #print("Making red's move...")
#                 moves = redPlayer.best_move(board)
#                 for index, move in enumerate(moves):
#                     moves[index] = [index, move]
#                 moves = sorted(moves, key=lambda x: x[1])
#                 for j in range(7):
#                     try:
#                         board.make_move(moves[j][0])
#                         break
#                     except:
#                         pass
#             else:
#                 #print("Making black's move...")
#                 moves = blackPlayer.best_move(board)
#                 for index, move in enumerate(moves):
#                     moves[index] = [index, move]
#                 moves = sorted(moves, key=lambda x: x[1])
#                 for j in range(7):
#                     try:
#                         board.make_move(moves[j][0])
#                         break
#                     except:
#                         pass
#             #board.print()
#
#         #here. find out who won. record this.
#         if board.won:
#             if play % 2 == 1:
#                 if board.won_by == 1:
#                     wins["ai"] += 1
#                 else:
#                     wins["opponent"] += 1
#             else:
#                 if board.won_by == 1:
#                     wins["opponent"] += 1
#                 else:
#                     wins["ai"] += 1
#             if wins["ai"] == 5 or wins["opponent"] == 5:
#                 done_playing = True
#                 if wins["ai"] == 5 and wins["opponent"] < 3:
#                     print(wins)
#                     print("My opponent was sucky!")
#                     var = math.floor(i/10)*10
#                     if var not in upgrade_index:
#                         upgrade_index.append(var)
#                         upgrades.append(0)
#                 elif wins["opponent"] == 5 and wins["ai"] < 3:
#                     ai = deepcopy(opponent)
#                     print(wins)
#                     print("Found a slightly better AI!")
#                     var = math.floor(i/10)*10
#                     if var not in upgrade_index:
#                         upgrade_index.append(var)
#                         upgrades.append(1)
#                     else:
#                         upgrades[int(math.floor(i/10))] += 1
#                 else:
#                     print(wins)
#                     print("My opponent was about the same level as me...")
#                     var = math.floor(i/10)*10
#                     if var not in upgrade_index:
#                         upgrade_index.append(var)
#                         upgrades.append(0)
#
# ai_file = open("AIstoragefile_test", "wb")
# pickle.dump(ai, ai_file)
#
# plot_data = [upgrade_index, upgrades]
# plt.plot(plot_data[0], plot_data[1], label="Train")
# plt.legend()
# plt.show()


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
        moves = ai.best_move(game)
        for index, move in enumerate(moves):
            moves[index] = [index, move]
        moves = sorted(moves, key=lambda x: x[1], reverse=True)
        for i in range(7):
            try:
                game.make_move(moves[i][0])
                break
            except:
                pass

game = GameBoard.GameBoard()
while not (game.won or game.tied):
    if game.whoseTurn() == 2:
        game.print()
        move = int(input("What is your move?"))
        print("Making red's move...")
        game.make_move(move)
    else:
        print("Making black's move...")
        moves = ai.best_move(game)
        for index, move in enumerate(moves):
            moves[index] = [index, move]
        moves = sorted(moves, key=lambda x: x[1], reverse=True)
        for i in range(7):
            try:
                game.make_move(moves[i][0])
                break
            except:
                pass


game = GameBoard.GameBoard()
while not (game.won or game.tied):
    if game.whoseTurn() == 2:
        game.print()
        move = int(input("What is your move?"))
        print("Making black's move...")
        game.make_move(move)
    else:
        print("Making red's move...")
        if game.count < 2:
            game.make_move(random.randint(0,6))
            continue
        next_boards = ai.get_next_boards(game) + ai.get_next_boards(game, True)
        targets = []
        for i in range(14):
            if next_boards[i] is None:
                targets.append(0)
                continue
            pieces_in_a_row = ai.get_board_pieces_in_a_row(next_boards[i])
            red = pieces_in_a_row[1]
            black = pieces_in_a_row[2]
            priority = 0.7
            if i <= 6:
                color = game.whoseTurn()
            else:
                color = (game.whoseTurn() - 1.5) * -1 + 1.5
                priority = 1
            if color == 1:
                targets.append(((red / black - 0.25) / 3.75) * priority)
            elif color == 2:
                targets.append(((black / red - 0.25) / 3.75) * priority)
            else:
                raise Exception("You got a color that doesn't exist!")
        n_targets = []
        for i in range(14):
            n_targets.append(targets[i] / np.sum(targets))
        print(n_targets)
        formatted_prediction = []
        for i in range(7):
            formatted_prediction.append((n_targets[i] + n_targets[i + 7]) / 2)
        print(formatted_prediction)
        for index, move in enumerate(formatted_prediction):
            formatted_prediction[index] = [index, move]
        moves = sorted(formatted_prediction, key=lambda x: x[1], reverse=True)
        print(moves)
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


