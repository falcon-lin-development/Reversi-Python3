import unittest
import othello


class tests(unittest.TestCase):

    def test_eat_all(self):
        test = othello.OthelloGame(8)
        for vertical_index, row in enumerate(test.board):
            for horizontal_index, chess in enumerate(row):
                if vertical_index == 0 or horizontal_index == 0 or vertical_index == test.size_of_board-1 or horizontal_index == test.size_of_board-1:
                    chess.chess_type = othello.Chess.BLACK
                elif vertical_index == 5 and horizontal_index == 5:
                    chess.chess_type = othello.Chess.EMPTY
                else:
                    chess.chess_type = othello.Chess.WHITE
        print(test)
        self.assertTrue(test.move(5, 5))
        print(test)
        for row in test.board:
            for chess in row:
                self.assertEqual(chess.get_type(), othello.Chess.BLACK)


if __name__ == "__main__":
    unittest.main()
