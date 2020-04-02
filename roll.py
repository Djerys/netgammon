import random


class Roll:
    def __init__(self, die1=None, die2=None):
        if die1 is None:
            die1 = random.randint(1, 6)
        if die2 is None:
            die2 = random.randint(1, 6)
        assert 1 <= die1 <= 6, f'Invalid roll: {die1}'
        assert 1 <= die2 <= 6, f'Invalid roll: {die2}'
        self.die1, self.die2 = die1, die2
        if die1 == die2:
            self._dies = (die1, die1, die1, die1)
        else:
            self._dies = (die1, die2)

    @property
    def dies(self):
        return self._dies

    def __repr__(self):
        return f'{self.die1}x{self.die2}'

    def __hash__(self):
        return hash(self.die1) + hash(self.die2)

    def __eq__(self, other):
        return self.die1 == other.die1 and self.die2 == other.die2
