import sys

import pygame
import ecys

import config
import logic
import graphic
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
                    render.image = config.DIE_IMAGES[self.game.roll.die1]
                elif die.number == 2:
                    render.image = config.DIE_IMAGES[self.game.roll.die2]


@ecys.requires(c.Render, logic.Piece)
class ArrangePiecesSystem(ecys.System):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def update(self):
        for point in self.game.board.points[1:25]:
            piece_number = 0
            for piece in point.pieces:
                piece_entity = self._piece_entity(piece)
                render = piece_entity.get_component(c.Render)
                coords = graphic.PIECE_COORDS[point.number, piece_number]
                render.rect.x, render.rect.y = coords
                render.visible = True
                piece_number += 1

    def _piece_entity(self, piece):
        entities = self.world.entities_with(logic.Piece)
        for entity in entities:
            if piece == entity.get_component(logic.Piece):
                return entity


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
                    point.color == self.game.color):
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
                self.clicked_from[0].clicked = False
                self.clicked_from[1].visible = False
                self.clicked_from = None
                clicked = True
                point = entity.get_component(logic.Point)

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
        if not self.game.history or not self.game.roll.dies:
            self.game.roll_dice()


class HintSystem(ecys.System):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def update(self):
        point_entity = self._from_point()
        if not point_entity:
            return
        point = point_entity.get_component(logic.Point)
        render = point_entity.get_component(c.Render)
        try:
            possible_points = self.game.board.possible_moves(
                self.game.roll, point.number
            )
            render.visible = True
            self._make_visible_possibles(possible_points)
        except AssertionError:
            pass

    def _from_point(self):
        point = None
        entities = self.world.entities_with(c.FromPointInput)
        for entity in entities:
            input = entity.get_component(c.FromPointInput)
            if input.clicked:
                point = entity
        return point

    def _make_visible_possibles(self, possible_points):
        entities = self.world.entities_with(c.ToPoint, c.Render, logic.Point)
        for entity in entities:
            number = entity.get_component(logic.Point).number
            if number in possible_points:
                render = entity.get_component(c.Render)
                render.visible = True


class MoveSystem(ecys.System):
    def update(self):
        pass
