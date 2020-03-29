import config as c
from game import Game
from checker import Checker


game = Game(c.CAPTION, c.SCREEN_WIDTH, c.SCREEN_HEIGHT, c.BACKGROUND_IMAGE, c.FRAME_RATE)
game.run()
