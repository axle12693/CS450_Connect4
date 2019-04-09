import Topology
import Network
import random
import GameBoard
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import time
from scipy.spatial import distance
import math


class C4NN:
    def __init__(self):
        # eventually, we will create the network here.
        top = Topology.Topology()
        top.add_layer(85, "Input")
        top.add_layer(672)
        top.add_layer(336)
        top.add_layer(14)
        self.net = Network.Network(top, learning_rate=0.0001)

    def mutate(self, ls=None):
        if ls is None:
            ls = self.net.weights
        for index, el in enumerate(ls):
            if type(el) == type([]):
                ls[index] = self.mutate(ls[index])
            else:
                ls[index] = el + random.uniform(-1, 1)
                if ls[index] > 10:
                    ls[index] = 10
                if ls[index] < -10:
                    ls[index] = -10
        return ls

    def get_next_boards(self, board, force_opponent_move=False):
        next_boards = [None, None, None, None, None, None, None]

        for i in range(7):
            board_copy = deepcopy(board)
            try:
                board_copy.make_move(i, suppress_won_message=True, force_opponent_move=force_opponent_move)
                next_boards[i] = board_copy
            except GameBoard.GameFinishedException:
                if board_copy.tied:
                    pass # leave it as a 0
                elif board_copy.won:
                    next_boards[i] = None
            except GameBoard.FullColumnException:
                pass #leave it as a 0
        return next_boards

    def board_to_vector(self, board, turn):
        board_vector = []
        for i in range(6):
            board_vector += board.board[i]
        one_hot_board_vector = []
        for el in board_vector:
            if el == 0:
                one_hot_board_vector += [0, 0]
            elif el == 1:
                one_hot_board_vector += [1, 0]
            else:
                one_hot_board_vector += [0, 1]
        one_hot_board_vector += [turn]
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
                        board.next_boards[i-1].score = board.next_boards_scores[i-1]
                    break
        else:
            board.next_boards = self.get_next_boards(board)
            board.next_boards_scores = []
            board.expanded = True
            for index, b in enumerate(board.next_boards):
                if b == 0:
                    board.next_boards_scores.append(0)
                    if board.next_boards[index] not in (0, 1, 2):
                        board.next_boards[index].score = board.next_boards_scores[index]
                    continue
                elif b == 1:
                    if board.whoseTurn() == 1:
                        board.next_boards_scores.append(0)
                        if board.next_boards[index] not in (0, 1, 2):
                            board.next_boards[index].score = board.next_boards_scores[index]
                    else:
                        board.next_boards_scores.append(1)
                        if board.next_boards[index] not in (0, 1, 2):
                            board.next_boards[index].score = board.next_boards_scores[index]
                    continue
                elif b == 2:
                    if board.whoseTurn() == 2:
                        board.next_boards_scores.append(0)
                        if board.next_boards[index] not in (0, 1, 2):
                            board.next_boards[index].score = board.next_boards_scores[index]
                    else:
                        board.next_boards_scores.append(1)
                        if board.next_boards[index] not in (0, 1, 2):
                            board.next_boards[index].score = board.next_boards_scores[index]
                    continue
                board_vector = self.board_to_vector(b, b.whoseTurn() - 1)
                board.next_boards[index].score = self.net.predict(board_vector)[0]
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
                if board.next_boards[index] not in (0, 1, 2):
                    board.next_boards[index].score = board.next_boards_scores[index]
                continue
            elif b == 1:
                if board.whoseTurn() == 1:
                    board.next_boards_scores.append(0)
                    if board.next_boards[index] not in (0, 1, 2):
                        board.next_boards[index].score = board.next_boards_scores[index]
                else:
                    board.next_boards_scores.append(1)
                    if board.next_boards[index] not in (0, 1, 2):
                        board.next_boards[index].score = board.next_boards_scores[index]
                continue
            elif b == 2:
                if board.whoseTurn() == 2:
                    board.next_boards_scores.append(0)
                    if board.next_boards[index] not in (0, 1, 2):
                        board.next_boards[index].score = board.next_boards_scores[index]
                else:
                    board.next_boards_scores.append(1)
                    if board.next_boards[index] not in (0, 1, 2):
                        board.next_boards[index].score = board.next_boards_scores[index]
                continue
            board_vector = self.board_to_vector(b, b.whoseTurn() - 1)
            board.next_boards[index].score = self.net.predict(board_vector)[0]
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
                        board.next_boards[i-1].score = 0
                    else:
                        board.next_boards_scores[i-1] = self.expand_once(b)
                        board.next_boards[i-1].score = board.next_boards_scores[i-1]
                    break

    def best_move(self, board, time_limit=1000):
        board_copy = deepcopy(board)
        board_vec = self.board_to_vector(board_copy, board_copy.whoseTurn() - 1)
        prediction = self.net.predict(board_vec)
        formatted_prediction = []
        for i in range(7):
            formatted_prediction.append((prediction[i] + prediction[i+7]) / 2)
        return formatted_prediction



        # run_until = math.floor(time.time() * 1000) + time_limit
        # self.expand(board_copy, run_until)
        # return np.argmax(board_copy.next_boards_scores)


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
        print("Generating boards...")
        training_boards_list = []
        boards0 = []
        boards1 = []
        boards2 = []
        boards3 = []
        boards4 = []
        boards5 = []
        while len(boards0) < num_boards / 6:
            num_moves = random.randint(2,7)
            board = GameBoard.GameBoard()
            for _ in range(num_moves):
                try:
                    board.make_move(random.randint(0,6), suppress_won_message=True)
                except:
                    pass
            if board.won or board.tied or board.count < 2:
                continue
            boards0.append(board)
        while len(boards1) < num_boards / 6:
            num_moves = random.randint(8,14)
            board = GameBoard.GameBoard()
            for _ in range(num_moves):
                try:
                    board.make_move(random.randint(0,6), suppress_won_message=True)
                except:
                    pass
            if board.won or board.tied or board.count < 2:
                continue
            boards1.append(board)
        while len(boards2) < num_boards / 6:
            num_moves = random.randint(15,21)
            board = GameBoard.GameBoard()
            for _ in range(num_moves):
                try:
                    board.make_move(random.randint(0,6), suppress_won_message=True)
                except:
                    pass
            if board.won or board.tied or board.count < 2:
                continue
            boards2.append(board)
        while len(boards3) < num_boards / 6:
            num_moves = random.randint(22,28)
            board = GameBoard.GameBoard()
            for _ in range(num_moves):
                try:
                    board.make_move(random.randint(0,6), suppress_won_message=True)
                except:
                    pass
            if board.won or board.tied or board.count < 2:
                continue
            boards3.append(board)
        while len(boards4) < num_boards / 6:
            num_moves = random.randint(29, 35)
            board = GameBoard.GameBoard()
            for _ in range(num_moves):
                try:
                    board.make_move(random.randint(0,6), suppress_won_message=True)
                except:
                    pass
            if board.won or board.tied or board.count < 15:
                continue
            boards4.append(board)
        while len(boards5) < num_boards / 6:
            num_moves = random.randint(36,42)
            board = GameBoard.GameBoard()
            for _ in range(num_moves):
                try:
                    board.make_move(random.randint(0,6), suppress_won_message=True)
                except:
                    pass
            if board.won or board.tied or board.count < 29:
                continue
            boards5.append(board)
        training_boards_list = boards0 + boards1 + boards2 + boards3 + boards4 + boards5
        print("Generated boards...")
        board_vector_list = []
        targets_list = []
        print("Creating data...")
        for training_board in training_boards_list:
            next_boards = self.get_next_boards(training_board) + self.get_next_boards(training_board, True)
            board_vector = self.board_to_vector(training_board, training_board.whoseTurn() - 1)
            board_vector_list.append(board_vector)
            targets = []
            for i in range(14):
                if next_boards[i] is None:
                    targets.append(0)
                    continue
                pieces_in_a_row = self.get_board_pieces_in_a_row(next_boards[i])
                red = pieces_in_a_row[0]
                black = pieces_in_a_row[1]
                priority = 0.99
                if i <= 6:
                    color = training_board.whoseTurn()
                    priority = 1
                else:
                    color = (training_board.whoseTurn() - 1.5) * -1 + 1.5
                if color == 1:
                    # targets.append(((red/black - 0.25) / 3.75) * priority)
                    targets.append((red[0] * 4 + red[1] + 9 + red[2] * 16) / (black[0] * 4 + black[1] + 9 + black[2] * 16))
                elif color == 2:
                    # targets.append(((black/red - 0.25) / 3.75) * priority)
                    targets.append((black[0] * 4 + black[1] + 9 + black[2] * 16) / (red[0] * 4 + red[1] + 9 + red[2] * 16))
                else:
                    raise Exception("You got a color that doesn't exist!")
            n_targets = []
            for i in range(14):
                n_targets.append(targets[i] / np.sum(targets))
            targets_list.append(n_targets)
        # for i in range(len(training_boards_list)):
        #     training_boards_list[i].print()
        #     print(training_boards_list[i].whoseTurn())
        #     print(targets_list[i])
        #     formatted_prediction = []
        #     for j in range(7):
        #         formatted_prediction.append((targets_list[i][j] + targets_list[i][j + 7]) / 2)
        #     print(formatted_prediction)
        print("Created data...")
        x_train, x_test, y_train, y_test = train_test_split(board_vector_list, targets_list, test_size=0.3)

        plot_data = self.net.fit(x_train, y_train, x_test, y_test, num_epochs=num_epochs)
        plt.plot(plot_data[0], plot_data[1], label="Train")
        plt.plot(plot_data[0], plot_data[2], label="Test")
        plt.legend()
        plt.show()


    def get_board_pieces_in_a_row(self, board):
        red_2 = 0
        red_3 = 0
        red_4 = 0
        black_2 = 0
        black_3 = 0
        black_4 = 0

        for y in range(6):
            for x in range(7):
                if board.board[y][x] == 0:
                    continue
                measuring = board.board[y][x]
                for el in board.check_won((y,x), suppress_message=True):
                    if el == 2:
                        if board.whoseTurn() == 1:
                            red_2 += 1
                        elif board.whoseTurn() == 2:
                            black_2 += 1
                    elif el == 3:
                        if board.whoseTurn() == 1:
                            red_3 += 1
                        elif board.whoseTurn() == 2:
                            black_3 += 1
                    elif el > 3:
                        if board.whoseTurn() == 1:
                            red_4 += 1
                        elif board.whoseTurn() == 2:
                            black_4 += 1
                # new_max_pieces = max(board.check_won((y, x), suppress_message=True))
                # if max_pieces[measuring] < new_max_pieces:
                #     max_pieces[measuring] = new_max_pieces
        max_pieces = [[red_2, red_3, red_4], [black_2, black_3, black_4]]
        return max_pieces




