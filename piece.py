import piece_color


class Piece:
    def __init__(self, color, number):
        assert color in {piece_color.WHITE, piece_color.RED}, \
            f'Color must be {piece_color.WHITE} or {piece_color.RED}: {color}'
        assert 1 <= number <= 15, f'Number out of range [1..15]: {number}'
        self._color = color
        self._number = number

    @property
    def color(self):
        return self._color

    @property
    def number(self):
        return self._number

    def __eq__(self, other):
        return self.color == other.color and self.number == other.number

    def __hash__(self):
        return hash(self.color) + hash(self.number)
