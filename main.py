from backgammon import Backgammon
from backgammon_client import BackgammonClient

import logic


game = Backgammon()
# point = game.board.points[25]
# for i in range(1, 16):
#     point.push(logic.Piece('W', i))
game_client = BackgammonClient(game)
game_client.run()
