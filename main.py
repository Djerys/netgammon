from backgammon import Backgammon
from backgammon_client import BackgammonClient

game = Backgammon()
game_client = BackgammonClient(game)
game_client.run()
