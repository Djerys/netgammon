from copy import deepcopy

import ecys

import logic
import config
import color
import graphic
import system as s
import component as c
from game import Game


class Backgammon(Game):
    def __init__(self):
        super().__init__(
            config.CAPTION, config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT, config.FRAME_RATE
        )
        self.board = logic.Board()
        self.history = []
        self.world = self._create_world()
        self.players = {}

    @property
    def roll(self):
        return self.history[-1].roll

    @property
    def color(self):
        return color.RED if len(self.history) % 2 == 0 else color.WHITE

    @property
    def moves(self):
        return self.history[-1].moves

    @property
    def possible_points(self):
        bar = self.board.bar(self.color)
        if bar.pieces:
            return [bar]
        points = [p for p in self.board.points]
        possible_points_ = []
        for point in points:
            if (point.pieces and point.color == self.color
                    and self.board.possible_moves(self.roll, point)):
                possible_points_.append(point)
        return possible_points_

    def move(self, from_point, to_point):
        if isinstance(from_point, logic.Point):
            from_point = from_point.number
        if isinstance(to_point, logic.Point):
            to_point = to_point.number
        self.board.move(from_point, to_point)
        dies = abs(from_point - to_point)
        self.roll.use(dies)
        self.moves.append((from_point, to_point))

    def roll_dice(self, roll=None):
        self.history.append(logic.Turn(roll or logic.Roll(), []))

    def _create_world(self):
        world = ecys.World()
        render_system = s.RenderSystem(self.surface, config.BACKGROUND_IMAGE)
        world.add_system(s.RollSystem(self), priority=5)
        world.add_system(s.ArrangeDiesSystem(self), priority=4)
        world.add_system(s.ArrangePiecesSystem(self), priority=3)
        world.add_system(s.InputSystem(self), priority=2)
        world.add_system(s.HintSystem(self), priority=1)
        world.add_system(render_system,  priority=0)
        self._create_points(world)
        self._create_pieces(world)
        self._create_dies(world)
        return world

    def _update(self):
        self.world.update()

    @staticmethod
    def _create_dies(world):
        world.create_entity(
            c.Render(coords=graphic.DICE_COORDS[color.RED, 1]),
            c.Die(color.RED, 1)
        )
        world.create_entity(
            c.Render(coords=graphic.DICE_COORDS[color.RED, 2]),
            c.Die(color.RED, 2)
        )
        world.create_entity(
            c.Render(coords=graphic.DICE_COORDS[color.WHITE, 1]),
            c.Die(color.WHITE, 1)
        )
        world.create_entity(
            c.Render(coords=graphic.DICE_COORDS[color.WHITE, 2]),
            c.Die(color.WHITE, 2)
        )

    def _create_pieces(self, world):
        for point in self.board.points:
            for piece in point.pieces:
                if point.color == color.RED:
                    image = config.RED_PIECE_IMAGE
                else:
                    image = config.WHITE_PIECE_IMAGE
                world.create_entity(
                    c.Render(image),
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
                c.Render(image, graphic.FROM_COORDS[point.number]),
                c.FromPointInput(),
                point
            )

    def _create_to_points(self, world):
        image = config.TO_IMAGE
        for point in self.board.points:
            world.create_entity(
                c.Render(image, graphic.TO_COORDS[point.number]),
                c.ToPoint(),
                point
            )


if __name__ == '__main__':
    game = Backgammon()
    game.roll_dice(logic.Roll(2, 5))
    game.run()
