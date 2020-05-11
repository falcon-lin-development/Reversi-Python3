from enum import Enum


class Chess():
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def __init__(self, chess_type, pos):
        horizontal_index, vertical_index = pos
        self.chess_type = chess_type
        self.vertical_pointer = vertical_index
        self.horizontal_pointer = horizontal_index

    def __str__(self):
        if self.chess_type == self.EMPTY:
            return " "
        elif self.chess_type == self.BLACK:
            return "X"
        else:
            return "0"

    def place(self, chess_type):
        assert chess_type != self.EMPTY
        self.chess_type = chess_type

    def be_captured(self):
        assert self.chess_type != self.EMPTY
        if self.chess_type == self.BLACK:
            self.chess_type = self.WHITE  # black => white, white => black
        else:
            self.chess_type = self.BLACK

    def get_XY(self):
        return self.horizontal_pointer, self.vertical_pointer

    def get_type(self):
        return self.chess_type

    def is_empty(self):
        return self.get_type() == Chess.EMPTY


class OthelloGameRep:
    def __init__(self, size_of_board):

        self.size_of_board = size_of_board
        self.initBoard()

    def checkRE(self):
        re = self.size_of_board % 2 == 0
        if hasattr(self, 'board'):
            for row in self.board:
                for chess in row:
                    re = re and 0 <= chess.horizontal_pointer < self.size_of_board and 0 <= chess.vertical_pointer < self.size_of_board
        if not re:
            raise Exception("re violation")

    def initBoard(self):
        self.checkRE()
        small_center = (self.size_of_board - 1) // 2
        large_center = small_center + 1

        # Let 0 be empty, 1 be black, 2 be white,
        self.board = [[Chess(Chess.EMPTY, (i, j)) for i in range(self.size_of_board)]
                      for j in range(self.size_of_board)]
        self.board[small_center][small_center].place(Chess.WHITE)
        self.board[large_center][large_center].place(Chess.WHITE)
        self.board[small_center][large_center].place(Chess.BLACK)
        self.board[large_center][small_center].place(Chess.BLACK)

    def __str__(self):
        out = ""
        # add chess
        for row in self.board:
            out += "+-"*self.size_of_board + "+\n"
            for chess in row:
                out += "|" + chess.__str__()
            out += "|\n"
        out += "+-"*self.size_of_board + "+\n"
        return out

    __repr__ = __str__


class OthelloGame(OthelloGameRep):
    def __init__(self, size_of_board):
        super().__init__(size_of_board)
        self.black_to_move = True

    @staticmethod
    def start_game(size_of_board=8):
        assert isinstance(size_of_board, int) and size_of_board % 2 == 0
        this_game = OthelloGame(size_of_board)
        passed_move_flag = False
        while True:
            print("==========Section Divider============")
            print(this_game.get_who_move() + "'s Turn")
            # get user input
            possible_poses = this_game.get_plausible_poses()
            if len(possible_poses) == 0:
                print("No Place to move")
                this_game.pass_move()

                if not passed_move_flag:
                    # flag up
                    passed_move_flag = True
                    continue
                else:
                    # End Game Count Board
                    this_game._end_game()
                    break
            else:
                print(this_game)
                print("Please choose a move: ", possible_poses)
                # get x input
                select_x = this_game._save_input("Horizontal Index: ")
                if select_x == "surrender":
                    this_game._end_game(this_game.get_who_move())
                    break
                # get y input
                select_y = this_game._save_input("Virtical Index: ")
                if select_y == "surrender":
                    this_game._end_game(this_game.get_who_move())
                    break
                # run the game
                this_game.move(select_x, select_y)
                # put down the flag
                if passed_move_flag:
                    passed_move_flag = False
                continue

    def _save_input(self, phrase):
        while True:
            try:
                result = input(phrase)
                if result == "surrender":
                    return result
                else:
                    result = int(result)
                return result
            except ValueError:
                print("ValueError. Please insert one integer")
                continue

    def _end_game(self, surrender=None):
        # Count the board
        white_count = 0
        black_count = 0
        for row in self.board:
            for chess in row:
                if chess.get_type() == Chess.BLACK:
                    black_count += 1
                elif chess.get_type() == Chess.WHITE:
                    white_count += 1

        if surrender:
            print(surrender, " surrendered. Game Ended")
        elif white_count > black_count:
            print("WHITE won")
        elif white_count < black_count:
            print("BLACK won")
        else:
            print("Draw")
        print("White Count: ", white_count)
        print("Black Count: ", black_count)
        print("Game End Position")
        print(self)

    def move(self, pos_or_x, y=None):
        horizontal_index = None
        vertical_index = None
        pos = None
        if y == None and isinstance(pos_or_x, tuple):
            (horizontal_index, vertical_index) = pos_or_x
            pos = pos_or_x
        elif isinstance(pos_or_x, int) and isinstance(pos_or_x, int):
            horizontal_index = pos_or_x
            vertical_index = y
            pos = horizontal_index, vertical_index
        else:
            raise ValueError(
                "only accept pos tuple arg or two int args:\n {0} and {1} are not valid".format(pos_or_x, y))

        # check can_place
        if not (0 <= horizontal_index < self.size_of_board and 0 <= vertical_index < self.size_of_board):
            print("cannot place: out of board")
            return False
        if self._position_is_occupied(pos):
            print("cannot place: occupied")
            return False

        # init
        THIS_CHESS_TYPE = Chess.WHITE
        if self.black_to_move:
            THIS_CHESS_TYPE = Chess.BLACK

        #  can_eat
        can_eat = self._eat_top(
            THIS_CHESS_TYPE, (horizontal_index, vertical_index))
        can_eat = self._eat_top_right(
            THIS_CHESS_TYPE, (horizontal_index, vertical_index)) or can_eat
        can_eat = self._eat_right(
            THIS_CHESS_TYPE, (horizontal_index, vertical_index)) or can_eat
        can_eat = self._eat_right_bottom(
            THIS_CHESS_TYPE, (horizontal_index, vertical_index)) or can_eat
        can_eat = self._eat_bottom(
            THIS_CHESS_TYPE, (horizontal_index, vertical_index)) or can_eat
        can_eat = self._eat_bottom_left(
            THIS_CHESS_TYPE, (horizontal_index, vertical_index)) or can_eat
        can_eat = self._eat_left(
            THIS_CHESS_TYPE, (horizontal_index, vertical_index)) or can_eat
        can_eat = self._eat_left_top(
            THIS_CHESS_TYPE, (horizontal_index, vertical_index)) or can_eat

        if can_eat:
            # place chess and move on
            self.board[vertical_index][horizontal_index].place(THIS_CHESS_TYPE)
            self.black_to_move = not self.black_to_move
            return True
        else:
            print("cannot place: ", (horizontal_index, vertical_index))
            return False

    def pass_move(self):
        self.black_to_move = not self.black_to_move

    def get_who_move(self):
        if self.black_to_move:
            return "BLACK"
        else:
            return "WHITE"

    def get_plausible_poses(self):
        plausible_poses = []
        # init
        THIS_CHESS_TYPE = Chess.WHITE
        if self.black_to_move:
            THIS_CHESS_TYPE = Chess.BLACK

        for row in self.board:
            for chess in row:
                if self._can_place(THIS_CHESS_TYPE, chess):
                    plausible_poses.append(chess.get_XY())
        return plausible_poses

    def _can_place(self, this_chess_type, this_chess):
        if not this_chess.is_empty():
            return False

        if (self._eat_top(this_chess_type, this_chess.get_XY(), False)
            or self._eat_top_right(this_chess_type, this_chess.get_XY(), False)
            or self._eat_right(this_chess_type, this_chess.get_XY(), False)
            or self._eat_right_bottom(this_chess_type, this_chess.get_XY(), False)
            or self._eat_bottom(this_chess_type, this_chess.get_XY(), False)
            or self._eat_bottom_left(this_chess_type, this_chess.get_XY(), False)
            or self._eat_left(this_chess_type, this_chess.get_XY(), False)
                or self._eat_left_top(this_chess_type, this_chess.get_XY(), False)):
            return True
        else:
            return False

    def _position_is_occupied(self, pos):
        (horizontal_index, vertical_index) = pos
        return not self.board[vertical_index][horizontal_index].is_empty()

    def _see_and_process_chess(self, placed_chess_type, this_chess, capture_targets, do_eat=True) -> bool and None:
        if this_chess.get_type() == placed_chess_type:
            # see same type: break and start eating
            if len(capture_targets) == 0:
                # see nothing
                return False
            else:
                if do_eat:
                    for target in capture_targets:
                        target.be_captured()
                return True
        elif this_chess.get_type() == Chess.EMPTY:
            # see empty: break and no eating
            return False
        else:
            # see different type: mark as target and keep looping
            capture_targets.append(this_chess)
            return None

    def _eat_top(self, this_chess_type, pos, do_eat=True) -> bool:
        """capturinga and calculation are done tgt, much faster performance"""
        (horizontal_index, vertical_index) = pos
        capture_targets = []
        for j in range(vertical_index-1, -1, -1):
            # see a chess
            this_chess = self.board[j][horizontal_index]
            # process the chess
            result = self._see_and_process_chess(
                this_chess_type, this_chess, capture_targets, do_eat)
            if result:
                return True
            elif result == False:
                return False
            else:
                continue
        else:
            # outside the board
            return False

    def _eat_top_right(self, this_chess_type, pos, do_eat=True) -> bool:
        (horizontal_index, vertical_index) = pos
        capture_targets = []
        for i in range(min(vertical_index - 0, self.size_of_board-1 - horizontal_index)):
            this_chess = self.board[vertical_index -
                                    (i+1)][horizontal_index + (i+1)]
            result = self._see_and_process_chess(
                this_chess_type, this_chess, capture_targets, do_eat)
            if result:
                return True
            elif result == False:
                return False
            else:
                continue
        else:
            return False

    def _eat_right(self, this_chess_type, pos, do_eat=True) -> bool:
        (horizontal_index, vertical_index) = pos
        capture_targets = []
        for i in range(self.size_of_board-1 - horizontal_index):
            this_chess = self.board[vertical_index][horizontal_index + (i+1)]
            result = self._see_and_process_chess(
                this_chess_type, this_chess, capture_targets, do_eat)
            if result:
                return True
            elif result == False:
                return False
            else:
                continue
        else:
            return False

    def _eat_right_bottom(self, this_chess_type, pos, do_eat=True) -> bool:
        (horizontal_index, vertical_index) = pos
        capture_targets = []
        for i in range(min(self.size_of_board-1 - vertical_index, self.size_of_board-1 - horizontal_index)):
            this_chess = self.board[vertical_index +
                                    (i+1)][horizontal_index + (i+1)]
            result = self._see_and_process_chess(
                this_chess_type, this_chess, capture_targets, do_eat)
            if result:
                return True
            elif result == False:
                return False
            else:
                continue
        else:
            return False

    def _eat_bottom(self, this_chess_type, pos, do_eat=True) -> bool:
        (horizontal_index, vertical_index) = pos
        capture_targets = []
        for i in range(self.size_of_board-1 - vertical_index):
            this_chess = self.board[vertical_index + (i+1)][horizontal_index]
            result = self._see_and_process_chess(
                this_chess_type, this_chess, capture_targets, do_eat)
            if result:
                return True
            elif result == False:
                return False
            else:
                continue
        else:
            return False

    def _eat_bottom_left(self, this_chess_type, pos, do_eat=True) -> bool:
        (horizontal_index, vertical_index) = pos
        capture_targets = []
        for i in range(min(self.size_of_board-1 - vertical_index, horizontal_index - 0)):
            this_chess = self.board[vertical_index +
                                    (i+1)][horizontal_index - (i+1)]
            result = self._see_and_process_chess(
                this_chess_type, this_chess, capture_targets, do_eat)
            if result:
                return True
            elif result == False:
                return False
            else:
                continue
        else:
            return False

    def _eat_left(self, this_chess_type, pos, do_eat=True) -> bool:
        (horizontal_index, vertical_index) = pos
        capture_targets = []
        for i in range(horizontal_index - 0):
            this_chess = self.board[vertical_index][horizontal_index - (i+1)]
            result = self._see_and_process_chess(
                this_chess_type, this_chess, capture_targets, do_eat)
            if result:
                return True
            elif result == False:
                return False
            else:
                continue
        else:
            return False

    def _eat_left_top(self, this_chess_type, pos, do_eat=True) -> bool:
        (horizontal_index, vertical_index) = pos
        capture_targets = []
        for i in range(min(vertical_index - 0, horizontal_index - 0)):
            this_chess = self.board[vertical_index -
                                    (i+1)][horizontal_index - (i+1)]
            result = self._see_and_process_chess(
                this_chess_type, this_chess, capture_targets, do_eat)
            if result:
                return True
            elif result == False:
                return False
            else:
                continue
        else:
            return False
