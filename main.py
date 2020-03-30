from backgammon import Backgammon
from checker import Checker

game = Backgammon()
game.sprites.add(Checker(Checker.BLACK, 0))
game.run()
