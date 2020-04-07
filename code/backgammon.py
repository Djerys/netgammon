import sys

import pygame

from . import config as c
from .base import system
from .base.game import Game


class Renderable(system.Component):
    def __init__(self, image_filename):
        self.image = pygame.image.load(image_filename)
        self.rect = self.image.get_rect()


@system.requires(Renderable)
class RenderSystem(system.System):
    def __init__(self, width, height, background_filename):
        super().__init__()
        self.surface = pygame.display.set_mode((width, height))
        self.background_image = pygame.image.load(background_filename)

    def update(self):
        self.surface.blit(self.background_image, (0, 0))
        for entity in self.required_entities:
            graphic = entity.get_component(Renderable)
            self.surface.blit(graphic.image, graphic.rect)
        pygame.display.update()


class Backgammon(Game):
    def __init__(self):
        super().__init__(c.CAPTION, c.FRAME_RATE)

    def _create_world(self):
        world = system.World()
        render_system = RenderSystem(
            c.SCREEN_WIDTH, c.SCREEN_HEIGHT, c.BACKGROUND_IMAGE
        )
        world.add_system(render_system)
        return world

    def _update_world(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        self.world.update()


if __name__ == '__main__':
    Backgammon().run()
