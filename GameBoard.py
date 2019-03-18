class GameBoard:
    def __init__(self, state=[[0 for _ in range(7)] for _ in range(6)]):
        self.board = state  # just a 7x6 list
        self.count = 0
        for i in range(6):
            for j in range(7):
                if self.board[i][j] != 0:
                    self.count += 1
        self.won = False

    def make_move(self, place=0):
        if self.board[0][place] != 0:
            raise Exception("This column has already been filled up!")
        if self.won:
            raise Exception("This game has been won (or lost) already!")
        color = 1
        if self.count % 2 == 1:
            color = 2
        row = 0
        for i in range(5, -1, -1):
            if self.board[i][place] == 0:
                self.board[i][place] = color
                row = i
                break
        self.count += 1

        self.check_won((row, place))

    def check_won(self, tup):
        color = self.board[tup[0]][tup[1]]

        # check horizontal
        total_h = 1
        for left_loop in range(-1, -4, -1):
            if tup[1] + left_loop < 0:
                break
            if self.board[tup[0]][tup[1] + left_loop] == color:
                total_h += 1
            else:
                break
        for right_loop in range(1, 4):
            if tup[1] + right_loop > 6:
                break
            if self.board[tup[0]][tup[1] + right_loop] == color:
                total_h += 1
            else:
                break
        # check vertical
        total_v = 1
        for top_loop in range(-1, -4, -1):
            if tup[0] + top_loop < 0:
                break
            if self.board[tup[0] + top_loop][tup[1]] == color:
                total_v += 1
            else:
                break
        for bottom_loop in range(1, 4):
            if tup[0] + bottom_loop > 5:
                break
            if self.board[tup[0] + bottom_loop][tup[1]] == color:
                total_v += 1
            else:
                break
        # check rising_diag

        # check falling_diag

        if total_h >= 4 or total_v >= 4:
            self.won = True
            return True

