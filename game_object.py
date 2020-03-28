from abc import ABC, abstractmethod

from pygame.rect import Rect


class GameObject(ABC):
    def __init__(self, x, y, w, h):
        self.bounds = Rect(x, y, w, h)

    @property
    def left(self):
        return self.bounds.left

    @property
    def right(self):
        return self.bounds.right

    @property
    def top(self):
        return self.bounds.top

    @property
    def bottom(self):
        return self.bounds.bottom

    @property
    def center(self):
        return self.bounds.center

    @property
    def center_x(self):
        return self.bounds.centerx

    @property
    def center_y(self):
        return self.bounds.centery

    @abstractmethod
    def draw(self, surface):
        pass

    def update(self):
        pass
