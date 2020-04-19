from backgammon import Backgammon
from backgammon_client import BackgammonGameClient

import logic


game = Backgammon()
# point = game.board.points[25]
# for i in range(1, 16):
#     point.push(logic.Piece('W', i))
game_client = BackgammonGameClient(game)
game_client.run()
