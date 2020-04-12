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
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        self.visible = visible


class PointEventComponent(ecys.Component):
    FROM = 1
    TO = 2

    def __init__(self, type, clicked=False):
        self.type = type
        self.clicked = clicked


@ecys.requires(RenderComponent, logic.Piece)
class ArrangePiecesSystem(ecys.System):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def update(self):
        for point in game.board.points[1:25]:
            piece_number = 0
            for piece in point.pieces:
                piece_entity = self._piece_entity(piece)
                render = piece_entity.get_component(RenderComponent)
                render.rect.x, render.rect.y = graphic.PIECE_COORDS[
                    point.number,
                    piece_number
                ]
                render.visible = True
                piece_number += 1

    def _piece_entity(self, piece):
        entities = self.world.entities_with(logic.Piece)
        for entity in entities:
            if piece == entity.get_component(logic.Piece):
                return entity


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
            event.clicked = False
            if render.rect.collidepoint(position):
                event.clicked = True


@ecys.requires(PointEventComponent, RenderComponent, logic.Point)
class HintSystem(ecys.System):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def update(self):
        from_point = self._from_point()
        if from_point is None:
            return
        render = from_point.get_component(RenderComponent)
        number = from_point.get_component(logic.Point).number
        try:
            possible_points = self.game.board.possible_moves(
                self.game.roll, number
            )
            render.visible = True
            self._make_visible_possibles(possible_points)
        except AssertionError:
            pass

    def _from_point(self):
        point = None
        for entity in self.entities:
            event = entity.get_component(PointEventComponent)
            render = entity.get_component(RenderComponent)
            render.visible = False
            if event.type == PointEventComponent.FROM and event.clicked:
                point = entity
        return point

    def _make_visible_possibles(self, possible_points):
        for entity in self.entities:
            number = entity.get_component(logic.Point).number
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
        self.world = self._create_world()

    @property
    def roll(self):
        return self.history[-1].roll

    @property
    def color(self):
        return color.RED if len(self.history) % 2 == 0 else color.WHITE

    @property
    def moves(self):
        return self.history[-1].moves

    def roll_dice(self, roll=None):
        self.history.append(logic.Turn(roll or logic.Roll(), []))

    def _create_world(self):
        world = ecys.World()
        render_system = RenderSystem(self.surface, config.BACKGROUND_IMAGE)
        world.add_system(ArrangePiecesSystem(self), priority=3)
        world.add_system(EventSystem(), priority=2)
        world.add_system((HintSystem(self)), priority=1)
        world.add_system(render_system,  priority=0)
        self._create_points(world)
        self._create_pieces(world)
        return world

    def _update(self):
        self.world.update()

    def _create_pieces(self, world):
        for point in self.board.points:
            for piece in point.pieces:
                if point.color == color.RED:
                    image = config.RED_PIECE_IMAGE
                else:
                    image = config.WHITE_PIECE_IMAGE
                world.create_entity(
                    RenderComponent(image),
                    piece
                )

    def _create_points(self, world):
        self._create_from_points(world)
        self._create_to_points(world)

    def _create_from_points(self, world):
        image = config.RED_FROM_IMAGE
        for point in self.board.points:
            if point.number >= 13:
                image = config.WHITE_FROM_IMAGE
            world.create_entity(
                RenderComponent(image, graphic.FROM_COORDS[point.number]),
                PointEventComponent(PointEventComponent.FROM),
                point
            )

    def _create_to_points(self, world):
        image = config.TO_IMAGE
        for point in self.board.points:
            world.create_entity(
                RenderComponent(image, graphic.TO_COORDS[point.number]),
                PointEventComponent(PointEventComponent.TO),
                point
            )


if __name__ == '__main__':
    game = Backgammon()
    game.roll_dice()
    print(game.roll)
    game.run()
