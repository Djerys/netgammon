from dataclasses import dataclass

import pygame
import ecys


class Render(ecys.Component):
    def __init__(self, image_filename=None, coords=(0, 0), visible=False):
        if image_filename:
            self._image = pygame.image.load(image_filename)
            self.rect = self._image.get_rect()
            self.rect.x, self.rect.y = coords
        else:
            self.rect = pygame.Rect(coords, (1, 1))
        self.visible = visible

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image_filename):
        self._image = pygame.image.load(image_filename)
        x, y = self.rect.x, self.rect.y
        self.rect = self._image.get_rect()
        self.rect.x, self.rect.y = x, y


@dataclass
class Move(ecys.Component):
    color: str
    from_point_number: int
    to_point_number: int


@dataclass
class FromPointInput(ecys.Component):
    clicked: bool = False


class ToPoint(ecys.Component):
    pass


@dataclass
class Die(ecys.Component):
    color: str
    number: int
