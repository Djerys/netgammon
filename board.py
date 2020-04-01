import piece_color

from piece import Piece
from point import Point


class Board:
    def __init__(self):
        self._points = tuple(Point(i) for i in range(26))
        white_start_state = ((1, 2), (12, 5), (17, 3), (19, 5))
        red_start_state = ((24, 2), (13, 5), (8, 3), (6, 5))
        self._pieces_on_start(piece_color.WHITE, white_start_state)
        self._pieces_on_start(piece_color.RED, red_start_state)

    def __copy__(self):
        pass

    def move(self, from_point, to_point):
        pass

    def possible_moves(self, roll, point):
        pass

    def _pieces_on_start(self, color, start_state):
        number = 1
        for point, count in start_state:
            for i in range(count):
                self.points[point].push(Piece(color, number))
                number += 1

    @property
    def points(self):
        return self._points
