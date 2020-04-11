import sys
from dataclasses import dataclass

import pygame
import ecys

import logic
import config
import color
from game import Game


class RenderComponent(ecys.Component):
    def __init__(self, image_filename, x=0, y=0, visible=True):
        self.image = pygame.image.load(image_filename)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.visible = visible


class PointEventComponent(ecys.Component):
    FROM = 1
    TO = 2

    def __init__(self, type, clicked=False):
        self.type = type
        self.clicked = clicked


@dataclass
class PointNumberComponent(ecys.Component):
    value: int


@ecys.requires(RenderComponent)
class RenderSystem(ecys.System):
    def __init__(self, surface, background_filename):
        super().__init__()
        self.surface = surface
        self.background_image = pygame.image.load(background_filename)

    def update(self):
        self.surface.blit(self.background_image, (0, 0))
        for entity in self.entities:
            render = entity.get_component(RenderComponent)
            if render.visible:
                self.surface.blit(render.image, render.rect)
        pygame.display.update()


class EventSystem(ecys.System):
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._handle_close_window()

            if event.type == pygame.MOUSEBUTTONUP:
                self._handle_press_on_point(event.pos)

    @staticmethod
    def _handle_close_window():
        pygame.quit()
        sys.exit()

    def _handle_press_on_point(self, position):
        entities = self.world.entities_with(PointEventComponent, RenderComponent)
        for entity in entities:
            event = entity.get_component(PointEventComponent)
            render = entity.get_component(RenderComponent)
            render.visible = False
            if render.rect.collidepoint(position):
                event.clicked = True


@ecys.requires(PointEventComponent, RenderComponent, PointNumberComponent)
class HintSystem(ecys.System):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def update(self):
        from_point = self._from_point()
        if from_point is None:
            return
        render = from_point.get_component(RenderComponent)
        render.visible = True
        number = from_point.get_component(PointNumberComponent).value
        possible_points = self.game.board.possible_moves(self.game.roll, number)
        self._make_visible_possibles(possible_points)

    def _from_point(self):
        for entity in self.entities:
            event = entity.get_component(PointEventComponent)
            if event.type == PointEventComponent.FROM and event.clicked:
                return entity
        return None

    def _make_visible_possibles(self, possible_points):
        for entity in self.entities:
            number = entity.get_component(PointNumberComponent).value
            if number in possible_points:
                render = entity.get_component(RenderComponent)
                render.visible = True


class Backgammon(Game):
    def __init__(self):
        super().__init__(
            config.CAPTION, config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT, config.FRAME_RATE
        )
        self.board = logic.Board()
        self.history = []

    @property
    def roll(self):
        return self.history[-1].roll

    @property
    def color(self):
        return color.RED if len(self.history) % 2 == 0 else color.WHITE

    @property
    def moves(self):
        return self.history[-1].moves

    def roll_dice(self):
        self.history.append(logic.Turn(logic.Roll(), []))

    def _create_world(self):
        world = ecys.World()
        render_system = RenderSystem(self.surface, config.BACKGROUND_IMAGE)
        world.add_system(render_system,  priority=0)
        world.add_system(EventSystem(), priority=1)
        world.create_entity(
            RenderComponent(config.DICE_IMAGES[1]),
            PointEventComponent(PointEventComponent.FROM)
        )
        return world

    def _update_world(self):
        self.world.update()


if __name__ == '__main__':
    Backgammon().run()
