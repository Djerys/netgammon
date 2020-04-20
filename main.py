from backgammon import Backgammon
from backgammon_client import BackgammonGameClient


game = Backgammon()
game_client = BackgammonGameClient(game)
game_client.run()
