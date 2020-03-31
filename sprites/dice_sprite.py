import pygame

import config


class DiceSprite(pygame.sprite.Sprite):
    def __init__(self, value=1):
        super().__init__()
        self.value = value
        self.image = pygame.image.load(config.DICE_IMAGES[value])
        self.rect = self.image.get_rect()
        self.rect.x = 150
        self.rect.y = 300
