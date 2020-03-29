import pygame

import config


class Checker(pygame.sprite.Sprite):
    WHITE = 0
    BLACK = 1

    def __init__(self, checker_color, point):
        pygame.sprite.Sprite.__init__(self)
        if checker_color == Checker.WHITE:
            image_filename = config.WHITE_CHECKER_IMAGE
        else:
            image_filename = config.BLACK_CHECKER_IMAGE
        self.image = pygame.image.load(image_filename).convert()
        self.point = point
        self.rect = self.image.get_rect()

    def update(self):
        pass
