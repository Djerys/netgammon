import sys
from dataclasses import dataclass

import pygame
import ecys

import logic
import config
from game import Game


class RenderComponent(ecys.Component):
    def __init__(self, image_filename, x=0, y=0, visible=True):
        self.image = pygame.image.load(image_filename)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.visible = visible


class PointEventComponent(ecys.Component):
    SOURCE = 1
    DESTINY = 2

    def __init__(self, what, clicked=False):
        self.what = what
        self.clicked = clicked


@dataclass
class TurnComponent(ecys.Component):
    turn: logic.Turn


@ecys.requires(RenderComponent)
class RenderSystem(ecys.System):
    def __init__(self, width, height, background_filename):
        super().__init__()
        self.surface = pygame.display.set_mode((width, height))
        self.background_image = pygame.image.load(background_filename)

    def update(self):
        self.surface.blit(self.background_image, (0, 0))
        for entity in self.required_entities:
            render = entity.get_component(RenderComponent)
            if render.visible:
                self.surface.blit(render.image, render.rect)
        pygame.display.update()


@ecys.requires(PointEventComponent, RenderComponent)
class PointEventHandlingSystem(ecys.System):
    def __init__(self):
        super().__init__()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                for entity in self.required_entities:
                    self._handle(entity, event.pos)

    @staticmethod
    def _handle(entity, position):
        clicked, visible = False, False
        event = entity.get_component(PointEventComponent)
        render = entity.get_component(RenderComponent)
        if render.rect.collidepoint(position):
            clicked, visible = True, True
        event.clicked = clicked
        render.visible = visible


class Backgammon(Game):
    def __init__(self):
        super().__init__(config.CAPTION, config.FRAME_RATE)

    def _create_world(self):
        world = ecys.World()
        render_system = RenderSystem(
            config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.BACKGROUND_IMAGE
        )
        world.add_system(render_system,  priority=0)
        world.add_system(PointEventHandlingSystem(), priority=1)
        world.create_entity(
            RenderComponent(config.DICE_IMAGES[1]),
            PointEventComponent(PointEventComponent.DESTINY)
        )
        return world

    def _update_world(self):
        self.world.update()


if __name__ == '__main__':
    Backgammon().run()
