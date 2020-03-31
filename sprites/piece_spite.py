import pygame

import config
import piece_color


class PieceSprite(pygame.sprite.Sprite):
    def __init__(self, color, point):
        super().__init__()
        if color == piece_color.WHITE:
            image_filename = config.WHITE_PIECE_IMAGE
        else:
            image_filename = config.RED_PIECE_IMAGE
        self.image = pygame.image.load(image_filename)
        self.point = point
        self.rect = self.image.get_rect()

    def update(self):
        pass
