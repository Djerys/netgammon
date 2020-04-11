import sys
from dataclasses import dataclass

import pygame
import ecys

import logic
import config
import color
import graphic
from game import Game


class RenderComponent(ecys.Component):
    def __init__(self, image_filename, coords=(0, 0), visible=False):
        self.image = pygame.image.load(image_filename)
        self.rect = self.image.get_rect()
        self.rect.centerx = coords[0]
        self.rect.centery = coords[1]
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

            if (event.type == pygame.MOUSEBUTTONUP and
                    event.button == pygame.BUTTON_LEFT):
                self._handle_point_press(event.pos)

    @staticmethod
    def _handle_close_window():
        pygame.quit()
        sys.exit()

    def _handle_point_press(self, position):
        entities = self.world.entities_with(PointEventComponent, RenderComponent)
        for entity in entities:
            event = entity.get_component(PointEventComponent)
            render = entity.get_component(RenderComponent)
            render.visible = False
            event.clicked = False
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
        number = from_point.get_component(PointNumberComponent).value
        try:
            possible_points = self.game.board.possible_moves(
                self.game.roll, number
            )
            render.visible = True
            self._make_visible_possibles(possible_points)
        except AssertionError:
            pass

    def _from_point(self):
        for entity in self.entities:
            event = entity.get_component(PointEventComponent)
            if event.type == PointEventComponent.FROM and event.clicked:
                return entity
        return None

    def _make_visible_possibles(self, possible_points):
        for entity in self.entities:
            number = entity.get_component(PointNumberComponent).value
            event = entity.get_component(PointEventComponent)
            if (event.type == PointEventComponent.TO and
                    number in possible_points):
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
        world.add_system(EventSystem(), priority=2)
        world.add_system((HintSystem(self)), priority=1)
        world.add_system(render_system,  priority=0)
        self._create_points(world)
        return world

    def _update_world(self):
        self.world.update()

    @staticmethod
    def _create_points(world):
        Backgammon._create_from_points(world)
        Backgammon._create_to_points(world)

    @staticmethod
    def _create_from_points(world):
        image = config.RED_FROM_IMAGE
        for i in range(1, 25):
            if i >= 13:
                image = config.WHITE_FROM_IMAGE
            world.create_entity(
                RenderComponent(image, graphic.FROM_COORDS[i]),
                PointEventComponent(PointEventComponent.FROM),
                PointNumberComponent(i)
            )

    @staticmethod
    def _create_to_points(world):
        image = config.TO_IMAGE
        for i in range(0, 26):
            world.create_entity(
                RenderComponent(image, graphic.TO_COORDS[i], True),
                PointEventComponent(PointEventComponent.TO),
                PointNumberComponent(i)
            )


if __name__ == '__main__':
    game = Backgammon()
    game.roll_dice()
    print(game.roll)
    game.run()
