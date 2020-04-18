import logic
import color


class Backgammon:
    def __init__(self):
        self.board = logic.Board()
        self.history = []

    def restart(self):
        self.board.on_start()
        self.history = []

    @property
    def game_over(self):
        return self.board.finished

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
        if self.board.bar_pieces(self.color):
            if self.board.possible_moves(self.roll, bar):
                return [bar]
            else:
                return []
        possible_points_ = []
        for point in self.board.points[1:25]:
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
