import random
import operator

import color


class Piece:
    def __init__(self, piece_color, number):
        assert piece_color in {color.WHITE, color.RED}, \
            f'Color must be {color.WHITE} or {color.RED}: {color}'
        assert 1 <= number <= 15, f'Number out of range [1..15]: {number}'
        self._color = piece_color
        self._number = number

    def __repr__(self):
        return f'{self.color} No {self.number}'

    def __eq__(self, other):
        return self.color == other.color and self.number == other.number

    def __hash__(self):
        return hash(self.color) + hash(self.number)

    @property
    def color(self):
        return self._color

    @property
    def number(self):
        return self._number


class Point:
    def __init__(self, number):
        self._pieces = []
        self.number = number

    def __repr__(self):
        info = 'empty'
        if self.pieces:
            info = f'{self.color}{len(self.pieces)}'
        return f'{self.number}: {info}'

    def __lt__(self, other):
        return self.number < other.number

    def __gt__(self, other):
        return self.number > other.number

    def __le__(self, other):
        return self.number <= other.number

    def __ge__(self, other):
        return self.number >= other.number

    def __eq__(self, other):
        return self.number == self.number

    def __ne__(self, other):
        return self.number != self.number

    def __hash__(self):
        return hash(self.number)

    @property
    def pieces(self):
        return tuple(self._pieces)

    def push(self, piece):
        if piece not in self._pieces:
            self._pieces.append(piece)
            if self.number not in {0, 25}:
                assert {p.color for p in self.pieces} == {piece.color}, \
                    'Only pieces of same color allowed in a point'

    def pop(self):
        assert self._pieces, 'No pieces at this Point'
        return self._pieces.pop()

    def blocked(self, piece_color):
        return (self.number not in {0, 25} and
                piece_color != self.color and
                len(self._pieces) > 1)

    @property
    def color(self):
        color_ = None
        if self._pieces:
            colors = {p.color for p in self._pieces}
            if self.number == 0 and color.WHITE in colors:
                color_ = color.WHITE
            elif self.number == 25 and color.RED in colors:
                color_ = color.RED
            elif len(colors) == 1:
                color_ = self._pieces[0].color
            else:
                raise ValueError('More than on color in one point')
        return color_


class Board:
    def __init__(self):
        self._points = tuple(Point(i) for i in range(26))
        white_start_state = ((1, 2), (12, 5), (17, 3), (19, 5))
        red_start_state = ((24, 2), (13, 5), (8, 3), (6, 5))
        self._on_start(color.WHITE, white_start_state)
        self._on_start(color.RED, red_start_state)

    def __repr__(self):
        return f'Board{self.points}'

    @property
    def points(self):
        return self._points

    def move(self, from_point, to_point):
        if not isinstance(from_point, int):
            from_point = from_point.number
        assert 0 <= from_point <= 25, f'Valid points are [0..25]: {from_point}'
        from_point = self.points[from_point]
        if not isinstance(to_point, int):
            to_point = to_point.number
        assert 0 <= to_point <= 25, f'Valid points are [0..25]: {to_point}'
        to_point = self.points[to_point]
        bear_off = to_point in {
            self.bear_off(color.WHITE),
            self.bear_off(color.RED)
        }
        if not bear_off:
            assert not to_point.blocked(from_point.color), \
                'Cannot move to a blocked point'
        different_colors = from_point.color != to_point.color
        if to_point.pieces and different_colors and not bear_off:
            self.bar(to_point.color).push(to_point.pop())
        to_point.push(from_point.pop())

    def possible_moves(self, roll, point):
        if isinstance(point, int):
            assert 0 <= point <= 25, f'Valid points are [0..25]: {point}'
            point = self.points[point]
        assert point.pieces, f'There are no pieces on this point: {point}'
        piece = point.pieces[-1]
        direction = 1 if piece.color == color.WHITE else -1
        dies = roll.dies
        if not dies:
            return []
        if len(dies) == 1:
            paths = [(dies[0],)]
        elif dies[0] == dies[1]:
            paths = [(dies[0],) * len(dies)]
        else:
            paths = [(dies[0], dies[1]), (dies[1], dies[0])]
        many_in_bar = len(self.bar_pieces(piece.color)) > 1
        moves = []
        min_point = 1
        max_point = 24
        if self.can_bear_off(piece.color):
            if piece.color == color.RED:
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

    def can_bear_off(self, piece_color):
        points = range(19) if piece_color == color.WHITE else range(7, 26)
        for point in points:
            if piece_color == self.points[point].color:
                return False
        return True

    def finished(self):
        outer_whites = [p for p in self.bear_off(color.WHITE).pieces if
                        p.color == color.WHITE]
        outer_reds = [p for p in self.bear_off(color.RED).pieces if
                      p.color == color.RED]
        return len(outer_whites) == 15 or len(outer_reds) == 15

    def bar(self, piece_color):
        return self.points[0 if piece_color == color.WHITE else 25]

    def bar_pieces(self, piece_color):
        return tuple(
            p for p in self.bar(piece_color).pieces if
            p.color == piece_color
        )

    def bear_off(self, piece_color):
        return self.points[0 if piece_color == color.RED else 25]

    def bear_off_pieces(self, piece_color):
        return tuple(
            p for p in self.bear_off(piece_color).pieces if
            p.color == piece_color
        )

    def strongholds(self, piece_color):
        return [p for p in self.points if p.color == piece_color and len(p.pieces) > 1]

    def saved_pieces(self, piece_color):
        if piece_color == color.WHITE:
            enemy = color.RED
            behind = operator.gt
            last_point = max(i for i in range(25, 1, -1)
                             if self.points[i].color == enemy)
            enemy_line = self.points[last_point]
        else:
            enemy = color.WHITE
            behind = operator.lt
            last_point = max(i for i in range(24) if self.points[i].color == enemy)
            enemy_line = self.points[last_point]
        return [p for p in self.points if behind(p, enemy_line) and p.pieces]

    def exposed_pieces(self, piece_color):
        saved = self.saved_pieces(piece_color)
        bar = self.bar(piece_color)
        return [p for p in self.points if
                p.color == piece_color and
                len(p.pieces) == 1 and
                p not in saved and
                p != bar]

    def _on_start(self, piece_color, start_state):
        number = 1
        for point, count in start_state:
            for i in range(count):
                self.points[point].push(Piece(piece_color, number))
                number += 1


class Roll:
    def __init__(self, die1=None, die2=None):
        if die1 is None:
            die1 = random.randint(1, 6)
        if die2 is None:
            die2 = random.randint(1, 6)
        assert 1 <= die1 <= 6, f'Invalid roll: {die1}'
        assert 1 <= die2 <= 6, f'Invalid roll: {die2}'
        self.die1, self.die2 = die1, die2
        if die1 == die2:
            self._dies = (die1, die1, die1, die1)
        else:
            self._dies = (die1, die2)

    def __repr__(self):
        return f'{self.die1}x{self.die2}'

    def __hash__(self):
        return hash(self.die1) + hash(self.die2)

    def __eq__(self, other):
        return self.die1 == other.die1 and self.die2 == other.die2

    @property
    def dies(self):
        return self._dies

    def use(self, move):
        dies_to_use = list(self.dies)
        if move in dies_to_use:
            dies_to_use.remove(move)
        else:
            while dies_to_use and move > max(dies_to_use):
                move -= dies_to_use.pop()
            if move != 0:
                raise ValueError('Impossible move')
        self._dies = tuple(dies_to_use)


class Turn:
    def __init__(self, roll, moves):
        self.roll = roll
        self.moves = moves

    def __repr__(self):
        return f'{self.roll}: {self.moves}'

    def __eq__(self, other):
        return self.roll == other.roll and self.moves == other.moves
