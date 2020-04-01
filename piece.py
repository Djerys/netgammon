from dataclasses import dataclass

import piece_color


@dataclass(unsafe_hash=True)
class Piece:
    _color: str
    _number: int

    def __post_init__(self):
        assert self.color in {piece_color.WHITE, piece_color.RED}, \
            f'Color must be {piece_color.WHITE} or {piece_color.RED}: {self.color}'
        assert 1 <= self.number <= 15, f'Number out of range [1..15]: {self.number}'

    @property
    def color(self):
        return self._color

    @property
    def number(self):
        return self._number
