class Turn:
    def __init__(self, roll, moves):
        self.roll = roll
        self.moves = moves

    def __repr__(self):
        return f'{self.roll}: {self.moves}'

    def __eq__(self, other):
        return self.roll == other.roll and self.moves == other.moves
