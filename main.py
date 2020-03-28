from game import Game
from checker import Checker

game = Game('Backgammon', 500, 600, 'backgammon_background.png', 60)
game.objects.append(Checker(300, 300, 30, (255, 255, 255), 0))
game.objects.append(Checker(100, 100, 30, (0, 0, 0), 0))
game.run()
