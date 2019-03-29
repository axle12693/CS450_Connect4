import Topology
import Network
import random
import GameBoard
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import time
import math


class C4NN:
    def __init__(self):
        # eventually, we will create the network here.
        top = Topology.Topology()
        top.add_layer(127, "Input")
        top.add_layer(64)
        top.add_layer(32)
        top.add_layer(16)
        top.add_layer(8)
        top.add_layer(4)
        top.add_layer(1)
        self.net = Network.Network(top)

    def mutate(self, ls=None):
        if ls is None:
            ls = self.net.weights
        for index, el in enumerate(ls):
            if type(el) == type([]):
                ls[index] = self.mutate(ls[index])
            else:
                ls[index] = el + random.uniform(-1, 1)
        return ls

    def get_next_boards(self, board):
        next_boards = [0,0,0,0,0,0,0]

        for i in range(7):
            board_copy = deepcopy(board)
            try:
                board_copy.make_move(i, suppress_won_message=True)
                next_boards[i] = board_copy
            except GameBoard.GameFinishedException:
                if board_copy.tied:
                    pass # leave it as a 0
                elif board_copy.won:
                    next_boards[i] = board_copy.won_by
            except GameBoard.FullColumnException:
                pass #leave it as a 0
        return next_boards

    def board_to_vector(self, board):
        board_vector = []
        for i in range(6):
            board_vector += board.board[i]
        one_hot_board_vector = []
        for el in board_vector:
            if el == 0:
                one_hot_board_vector += [1, 0, 0]
            elif el == 1:
                one_hot_board_vector += [0, 1, 0]
            else:
                one_hot_board_vector += [0, 0, 1]
        one_hot_board_vector += [board.whoseTurn() - 1]
        return one_hot_board_vector

    def expand_once(self, board):
        if board == 0 or board == 1 or board == 2:
            raise Exception("You really shouldn't get this. An int board was passed to expand_once.")
        if board.expanded:
            # Choose a random next_board to expand once (at this level, or if that is already done, at a future one)
            # This board will be picked probabilistically based on its "score".
            sum = np.sum(board.next_boards_scores)
            choice = random.uniform(0, sum)
            for i in range(1, 7):
                if choice <= np.sum(board.next_boards_scores[:i]):
                    b = board.next_boards[i - 1]
                    if b == 0 or b == 1 or b == 2:
                        pass
                    else:
                        board.next_boards_scores[i - 1] = self.expand_once(b)
                    break
        else:
            board.next_boards = self.get_next_boards(board)
            board.next_boards_scores = []
            board.expanded = True
            for index, b in enumerate(board.next_boards):
                if b == 0:
                    board.next_boards_scores.append(0)
                    continue
                elif b == 1:
                    if board.whoseTurn() == 1:
                        board.next_boards_scores.append(0)
                    else:
                        board.next_boards_scores.append(1)
                    continue
                elif b == 2:
                    if board.whoseTurn() == 2:
                        board.next_boards_scores.append(0)
                    else:
                        board.next_boards_scores.append(1)
                    continue
                board_vector = self.board_to_vector(b)
                board.next_boards[index].score = self.net.predict(board_vector)
                board.next_boards[index].expanded = False
                board.next_boards_scores.append(board.next_boards[index].score)
        return 1 - np.mean(board.next_boards_scores)

    def expand(self, board, run_until):
        board.next_boards = self.get_next_boards(board)
        # put the scores for next_boards into a single list, with assorted indices - corresponding to move numbers
        board.next_boards_scores = []
        board.expanded = True
        for index, b in enumerate(board.next_boards):
            if b == 0:
                board.next_boards_scores.append(0)
                continue
            elif b == 1:
                if board.whoseTurn() == 1:
                    board.next_boards_scores.append(0)
                else:
                    board.next_boards_scores.append(1)
                continue
            elif b == 2:
                if board.whoseTurn() == 2:
                    board.next_boards_scores.append(0)
                else:
                    board.next_boards_scores.append(1)
                continue
            board_vector = self.board_to_vector(b)
            board.next_boards[index].score = self.net.predict(board_vector)
            board.next_boards[index].expanded = False
            board.next_boards_scores.append(board.next_boards[index].score)
        while True:
            # print("choosing next_board to expand")
            if time.time() * 1000 >= run_until:
                return
            # Choose a random next_board to expand once (at this level, or if that is already done, at a future one)
            # This board will be picked probabilistically based on its "score".
            sum = np.sum(board.next_boards_scores)
            choice = random.uniform(0, sum)
            for i in range(1, 7):
                if choice <= np.sum(board.next_boards_scores[:i]):
                    b = board.next_boards[i-1]
                    if b == 0 or b == 1 or b == 2:
                        board.next_boards_scores[i-1] = 0
                    else:
                        board.next_boards_scores[i-1] = self.expand_once(b)
                    break

    def best_move(self, board, time_limit=100):
        board_copy = deepcopy(board)
        run_until = math.floor(time.time() * 1000) + time_limit
        self.expand(board_copy, run_until)
        return np.argmax(board_copy.next_boards_scores)


        # next_boards = [0,0,0,0,0,0,0]
        #
        # for i in range(7):
        #     board_copy = deepcopy(board)
        #     try:
        #         board_copy.make_move(i, suppress_won_message=True)
        #         next_boards[i] = board_copy
        #     except:
        #         next_boards[i] = None
        # scores = []
        # for index, next_board in enumerate(next_boards):
        #     if next_board is None:
        #         scores.append(-1)
        #         continue
        #     board_vector = []
        #     for i in range(6):
        #         board_vector += next_board.board[i]
        #     one_hot_board_vector = []
        #     for el in board_vector:
        #         if el == 0:
        #             one_hot_board_vector += [1, 0, 0]
        #         elif el == 1:
        #             one_hot_board_vector += [0, 1, 0]
        #         else:
        #             one_hot_board_vector += [0, 0, 1]
        #     one_hot_board_vector += [next_board.whoseTurn() - 1]
        #     scores.append(self.net.predict(one_hot_board_vector)[0])
        # return np.argmax(scores)

    def train_phase1(self, num_boards, num_epochs):
        # The first phase of training - this will be done entirely inside the class.
        # Requires that we first create the network.

        # Generate num_boards random, but valid, boards, along with targets
        print("Beginning train phase 1")
        boards_list = []
        board_vectors_list = []
        targets_list = []
        while len(boards_list) < num_boards:
            print("Boards_list is length " + str(len(boards_list)))
            board = GameBoard.GameBoard()
            for i in range(random.randint(1, 42)):
                try:
                    board.make_move(random.randint(0, 6))
                except:
                    break
            boards_list.append(board)
            board_vector = []
            for i in range(6):
                board_vector += board.board[i]
            one_hot_board_vector = []
            for el in board_vector:
                if el == 0:
                    one_hot_board_vector += [1, 0, 0]
                elif el == 1:
                    one_hot_board_vector += [0, 1, 0]
                else:
                    one_hot_board_vector += [0, 0, 1]
            one_hot_board_vector += [board.whoseTurn() - 1]
            board_vectors_list.append(one_hot_board_vector)
            pieces_in_a_row = self.get_board_pieces_in_a_row(board)
            red = pieces_in_a_row[1]
            black = pieces_in_a_row[2]
            if board.whoseTurn() == 1:
                targets_list.append([((red/black) - .25)/3.75])
            else:
                targets_list.append([((black/red) - .25)/3.75])

        # Split into training and testing
        x_train, x_test, y_train, y_test = train_test_split(board_vectors_list, targets_list, test_size=0.3)
        plot_data = self.net.fit(x_train, y_train, x_test, y_test, num_epochs)

        plt.plot(plot_data[0], plot_data[1], label="Train")
        plt.plot(plot_data[0], plot_data[2], label="Test")
        plt.xlabel = "Iteration"
        plt.ylabel = "Error"
        plt.title = "Diabetes"
        plt.text = "Diabetes"
        plt.legend()
        plt.show()

    def get_board_pieces_in_a_row(self, board):
        max_pieces = {1: 0, 2: 0}

        for y in range(6):
            for x in range(7):
                if board.board[y][x] == 0:
                    continue
                measuring = board.board[y][x]
                new_max_pieces = max(board.check_won((y, x)))
                if max_pieces[measuring] < new_max_pieces:
                    max_pieces[measuring] = new_max_pieces
        return max_pieces




