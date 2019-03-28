import Topology
import Network
import random
import GameBoard
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy


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

    def mutate(self, ls = None):
        if ls is None:
            ls = self.net.weights
        for index, el in enumerate(ls):
            if type(el) == type([]):
                ls[index] = self.mutate(ls[index])
            else:
                ls[index] = el + random.uniform(-1, 1)
        return ls

    def best_move(self, board):
        next_boards = [0,0,0,0,0,0,0]

        for i in range(7):
            board_copy = deepcopy(board)
            try:
                board_copy.make_move(i, suppress_won_message=True)
                next_boards[i] = board_copy
            except:
                next_boards[i] = None
        scores = []
        for index, next_board in enumerate(next_boards):
            if next_board is None:
                scores.append(-1)
                continue
            board_vector = []
            for i in range(6):
                board_vector += next_board.board[i]
            one_hot_board_vector = []
            for el in board_vector:
                if el == 0:
                    one_hot_board_vector += [1, 0, 0]
                elif el == 1:
                    one_hot_board_vector += [0, 1, 0]
                else:
                    one_hot_board_vector += [0, 0, 1]
            one_hot_board_vector += [next_board.whoseTurn() - 1]
            scores.append(self.net.predict(one_hot_board_vector)[0])
        return np.argmax(scores)

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




