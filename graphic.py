from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PointCoordinates(ABC):
    home_x: int = 288
    outer_x: int = 38
    x_step: int = 35

    @abstractmethod
    def __getitem__(self, point_number):
        pass


@dataclass
class FromPointCoordinates(PointCoordinates):
    red_y: int = 120
    white_y: int = 480

    def __getitem__(self, point_number):
        assert 1 <= point_number <= 24,\
            f'Source points in [1..24]: {point_number}'
        if 1 <= point_number <= 6:
            x = self.home_x + (6 - point_number) * self.x_step
            return x, self.red_y
        elif 7 <= point_number <= 12:
            x = self.outer_x + (12 - point_number) * self.x_step
            return x, self.red_y
        elif 13 <= point_number <= 18:
            x = self.outer_x + (point_number - 13) * self.x_step
            return x, self.white_y
        else:
            x = self.home_x + (point_number - 19) * self.x_step
            return x, self.white_y


FROM_COORDS = FromPointCoordinates()
