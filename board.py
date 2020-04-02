import operator

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

    def move(self, from_point, to_point):
        pass

    def possible_moves(self, roll, point):
        if isinstance(point, int):
            assert 0 <= point <= 25, f'Valid points are [0..25]: {point}'
            point = self.points[point]
        assert point.pieces, 'There are no pieces on this point'
        piece = point.pieces[-1]
        direction = 1 if piece.color == piece_color.WHITE else -1
        dies = roll.dies
        if not dies:
            return []
        if len(dies) == 1:
            paths = [(dies[0])]
        elif dies[0] == dies[1]:
            paths = [(dies[0]) * len(dies)]
        else:
            paths = [(dies[0], dies[1]), (dies[1], dies[0])]
        many_in_bar = len(self.bar_pieces(piece.color)) > 1
        moves = []
        min_point = 1
        max_point = 24
        if self.can_bear_off(piece.color):
            if piece.color == piece_color.RED:
                min_point -= 1
            else:
                max_point += 1
        for path in paths:
            if many_in_bar:
                path = path[:1]
            number = point.number
            for die in path:
                number += direction * die
                if (number < min_point or number > max_point or
                        self.points[number].blocked(piece.color)):
                    break
                if number not in moves:
                    moves.append(number)
        return sorted(moves)

    def can_bear_off(self, color):
        points = range(19) if color == piece_color.WHITE else range(7, 26)
        for point in points:
            if color == self.points[point].color:
                return False
        return True

    def finished(self):
        outer_whites = [p for p in self.outer(piece_color.WHITE).pieces if
                        p.color == piece_color.WHITE]
        outer_reds = [p for p in self.outer(piece_color.RED).pieces if
                      p.color == piece_color.RED]
        return len(outer_whites) == 15 or len(outer_reds) == 15

    def bar(self, color):
        return self.points[0 if color == piece_color.WHITE else 25]

    def bar_pieces(self, color):
        return tuple(p for p in self.bar(color).pieces if p.color == color)

    def outer(self, color):
        return self.points[0 if color == piece_color.RED else 25]

    def outer_pieces(self, color):
        return tuple(p for p in self.outer(color).pieces if p.color == color)

    def strongholds(self, color):
        return [p for p in self.points if p.color == color and len(p.pieces) > 1]

    def saved_pieces(self, color):
        if color == piece_color.WHITE:
            enemy = piece_color.RED
            behind = operator.gt
            last_point = max(i for i in range(25, 1, -1)
                             if self.points[i].color == enemy)
            enemy_line = self.points[last_point]
        else:
            enemy = piece_color.WHITE
            behind = operator.lt
            last_point = max(i for i in range(24) if self.points[i].color == enemy)
            enemy_line = self.points[last_point]
        return [p for p in self.points if behind(p, enemy_line) and p.pieces]

    def exposed_pieces(self, color):
        saved = self.saved_pieces(color)
        bar = self.bar(color)
        return [p for p in self.points if
                p.color == color and
                len(p.pieces) == 1 and
                p not in saved and
                p != bar]

    def _pieces_on_start(self, color, start_state):
        number = 1
        for point, count in start_state:
            for i in range(count):
                self.points[point].push(Piece(color, number))
                number += 1

    @property
    def points(self):
        return self._points
