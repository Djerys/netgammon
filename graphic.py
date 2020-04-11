from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PointCoordinates(ABC):
    width: int
    height: int
    red_y: int
    white_y: int
    home_x: int = 273
    outer_x: int = 23
    x_step: int = 35

    def __getitem__(self, point_number):
        if 1 <= point_number <= 6:
            x = self.home_x + (6 - point_number) * self.x_step
            return x, self.red_y
        if 7 <= point_number <= 12:
            x = self.outer_x + (12 - point_number) * self.x_step
            return x, self.red_y
        if 13 <= point_number <= 18:
            x = self.outer_x + (point_number - 13) * self.x_step
            return x, self.white_y
        if 19 <= point_number <= 24:
            x = self.home_x + (point_number - 19) * self.x_step
            return x, self.white_y


@dataclass
class FromPointCoordinates(PointCoordinates):
    width: int = 30
    height: int = 210
    red_y: int = 15
    white_y: int = 375

    def __getitem__(self, point_number):
        assert 1 <= point_number <= 24, \
            f'Number of source point in [1..24]: {point_number}'
        return super().__getitem__(point_number)


@dataclass
class ToPointCoordinates(PointCoordinates):
    width: int = 30
    height: int = 30
    red_y: int = 247
    white_y: int = 323
    bear_off_x: int = 455
    bear_off_y: int = 285

    def __getitem__(self, point_number):
        assert 0 <= point_number <= 25,\
            f'Number of destiny point in [0.25]: {point_number}'
        if point_number in (0, 25):
            return self.bear_off_x, self.bear_off_y
        return super().__getitem__(point_number)


FROM_COORDS = FromPointCoordinates()
TO_COORDS = ToPointCoordinates()
