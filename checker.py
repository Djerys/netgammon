import pygame

from game_object import GameObject


class Checker(GameObject):
    def __init__(self, x, y, radius, color, point):
        diameter = radius * 2
        super().__init__(x - radius, y - radius, diameter, diameter)
        self.radius = radius
        self.diameter = diameter
        self.color = color
        self.point = point

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.center, self.radius)

    def update(self):
        pass
