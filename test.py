from turn import Turn
from roll import Roll
from board import Board


board = Board()
roll = Roll()
moves = board.possible_moves(roll, 13)
print(roll)
print(moves)
print(board)
board.move(13, moves[0])
print(board)
