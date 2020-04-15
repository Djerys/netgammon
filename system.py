import sys
from functools import lru_cache

import pygame
import ecys

import config
import logic
import graphic
import color
import component as c


@ecys.requires(c.Render, c.Die)
class ArrangeDiesSystem(ecys.System):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def update(self):
        for entity in self.entities:
            render = entity.get_component(c.Render)
            die = entity.get_component(c.Die)
            if self.game.color == die.color:
                render.visible = True
                if die.number == 1:
                    render.image = config.DIE_IMAGES[die.color][self.game.roll.die1]
                elif die.number == 2:
                    render.image = config.DIE_IMAGES[die.color][self.game.roll.die2]
            else:
                render.visible = False


@ecys.requires(c.Render, logic.Piece)
class ArrangePiecesSystem(ecys.System):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def update(self):
        self._make_invisible_outside_pieces()
        self._arrange_inside_pieces()
        self._arrange_bar_banners()

    def _make_invisible_outside_pieces(self):
        points = self.game.board.points
        outside_points = (points[0], points[25])
        for point in outside_points:
            for piece in point.pieces:
                piece_entity = _entity_with_component(self, piece, logic.Piece)
                render = piece_entity.get_component(c.Render)
                render.visible = False

    def _arrange_bar_banners(self):
        bar = [
            (self.game.board.bar(color.WHITE),
             self.game.board.bar_pieces(color.WHITE)),
            (self.game.board.bar(color.RED),
             self.game.board.bar_pieces(color.RED))
        ]
        for point, pieces in bar:
            banner_entity = _entity_with_component(
                self, point, logic.Point, c.Banner
            )
            banner_render = banner_entity.get_component(c.Render)
            if pieces:
                banner_render.image = config.BANNER_IMAGES[len(pieces)]
                banner_render.visible = True
            else:
                banner_render.visible = False

    def _arrange_inside_pieces(self):
        for point in self.game.board.points[1:25]:
            for piece_number, piece in enumerate(point.pieces):
                piece_entity = _entity_with_component(self, piece, logic.Piece)
                piece_render = piece_entity.get_component(c.Render)
                coords = graphic.PIECE_COORDS[point.number, piece_number]
                piece_render.rect.x, piece_render.rect.y = coords
                if piece_number < config.VISIBLE_NUMBER:
                    piece_render.visible = True
                else:
                    piece_render.visible = False
            banner_entity = _entity_with_component(
                self, point, logic.Point, c.Banner
            )
            banner_render = banner_entity.get_component(c.Render)
            invisible_pieces = point.pieces[config.VISIBLE_NUMBER:]
            if invisible_pieces:
                number = len(invisible_pieces)
                banner_render.image = config.BANNER_IMAGES[number]
                banner_render.visible = True
            else:
                banner_render.visible = False


@ecys.requires(c.Render)
class RenderSystem(ecys.System):
    def __init__(self, surface, background_filename):
        super().__init__()
        self.surface = surface
        self.background_image = pygame.image.load(background_filename)

    def update(self):
        self.surface.blit(self.background_image, (0, 0))
        for entity in self.entities:
            render = entity.get_component(c.Render)
            if render.visible:
                self.surface.blit(render.image, render.rect)
        pygame.display.update()


class InputSystem(ecys.System):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.clicked_from = None

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._handle_close_window()

            if (event.type == pygame.MOUSEBUTTONUP and
                    event.button == pygame.BUTTON_LEFT):
                self._handle_from_point_press(event.pos)
                self._handle_to_point_press(event.pos)

    @staticmethod
    def _handle_close_window():
        pygame.quit()
        sys.exit()

    def _handle_from_point_press(self, position):
        from_entities = self.world.entities_with(
            c.FromPointInput, c.Render, logic.Point
        )
        other = []
        clicked = False
        for entity in from_entities:
            input = entity.get_component(c.FromPointInput)
            render = entity.get_component(c.Render)
            point = entity.get_component(logic.Point)
            if (render.rect.collidepoint(position) and
                    point in self.game.possible_points):
                render.visible = True
                self._make_to_points_invisible()
                input.clicked = True
                self.clicked_from = (input, render, point)
                clicked = True
            else:
                other.append((input, render))

        if clicked:
            for input, render in other:
                input.clicked = False
                render.visible = False

    def _handle_to_point_press(self, position):
        entities = self.world.entities_with(c.ToPoint, c.Render, logic.Point)
        clicked = False
        renders = []
        for entity in entities:
            render = entity.get_component(c.Render)
            renders.append(render)
            if (render.rect.collidepoint(position) and
                    render.visible and
                    self.clicked_from):
                point = entity.get_component(logic.Point)
                self.game.move(self.clicked_from[2], point)
                self.clicked_from[0].clicked = False
                self.clicked_from[1].visible = False
                self.clicked_from = None
                clicked = True

        if clicked:
            for render in renders:
                render.visible = False

    def _make_to_points_invisible(self):
        to_entities = self.world.entities_with(c.ToPoint, c.Render)
        for entity in to_entities:
            render = entity.get_component(c.Render)
            render.visible = False


class RollSystem(ecys.System):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def update(self):
        win_banner_entity = self.world.entities_with(
            c.WinBanner, c.Render
        )[0]
        render = win_banner_entity.get_component(c.Render)
        if self.game.board.finished:
            render.image = config.WIN_BANNER_IMAGES[self.game.color]
            render.visible = True
        else:
            render.visible = False

        if (not self.game.history or
                not self.game.roll.dies or
                not self.game.possible_points):
            self.game.roll_dice()


class HintSystem(ecys.System):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def update(self):
        point_entity = self._clicked_from_point()
        if not point_entity:
            return
        point = point_entity.get_component(logic.Point)
        try:
            possible_to_move = self.game.board.possible_moves(
                self.game.roll, point.number
            )
            self._make_visible_possibles(possible_to_move)
        except AssertionError:
            pass

    def _clicked_from_point(self):
        point_entity = None
        entities = self.world.entities_with(c.FromPointInput)
        for entity in entities:
            input = entity.get_component(c.FromPointInput)
            if input.clicked:
                point_entity = entity
        return point_entity

    def _make_visible_possibles(self, possible_points):
        entities = self.world.entities_with(c.ToPoint, c.Render, logic.Point)
        for entity in entities:
            number = entity.get_component(logic.Point).number
            if number in possible_points:
                render = entity.get_component(c.Render)
                render.visible = True


@lru_cache(maxsize=128)
def _entity_with_component(system, instance, *components):
    entities = system.world.entities_with(*components)
    for entity in entities:
        if instance == entity.get_component(components[0]):
            return entity
