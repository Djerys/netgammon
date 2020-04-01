import piece_color


class Point:
    def __init__(self, number):
        self._pieces = []
        self.number = number

    def __copy__(self):
        pass

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
        if piece not in self.pieces:
            self._pieces.append(piece)
            if self.number not in {0, 25}:
                assert {p.color for p in self.pieces} == {piece.color}, \
                    'Only pieces of same color allowed in a point'

    def pop(self):
        assert self.pieces, 'No pieces at this Point'
        return self._pieces.pop()

    def blocked(self, color):
        return (self.number not in {0, 25} and
                color != self.color and
                len(self.pieces) > 1)

    @property
    def color(self):
        color_ = None
        if self.pieces:
            colors = {p.color for p in self.pieces}
            if self.number == 0 and piece_color.WHITE in colors:
                color_ = piece_color.WHITE
            elif self.number == 25 and piece_color.RED in colors:
                color_ = piece_color.RED
            elif len(colors) == 1:
                color_ = self.pieces[0].color
            else:
                raise ValueError('More than on color in one point')
        return color_
