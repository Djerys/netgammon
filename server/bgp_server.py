# A server for a multi-player backgammon game. I created a
# new application-level protocol called BGP (Backgammon Game
# Protocol), which is entirely plain text. The messages of BGP are:
#
# Client -> Server
#   DIES <i> <i>
#   MOVE <i> <i>
#   ENDMOVE
#   QUIT
#
# Server -> Client
#   COLOR <c>
#   DIES <i> <i>
#   MOVE <i> <i>
#   ENDMOVE
#   QUIT
#
# Message's size is 10 byte.


import sys
import threading
import socketserver
import random


WHITE = 'W'
RED = 'R'


class QuitMessageException(Exception):
    pass


class PlayersCouple:
    _first_connected_player = None
    _couple_lock = threading.Lock()
    _colors = [WHITE, RED]

    def __init__(self):
        self.current_player = None
        self._lock = threading.Lock()

    def switch_current(self):
        with self._lock:
            self.current_player = self.current_player._opponent

    @classmethod
    def join(cls, player):
        with cls._couple_lock:
            if cls._first_connected_player is None:
                random.shuffle(cls._colors)
                player._color = cls._colors[0]
                player._couple = None
                cls._first_connected_player = player
            else:
                player1 = cls._first_connected_player
                player2 = player
                player2._color = cls._colors[1]
                player1._opponent = player2
                player2._opponent = player1
                couple = PlayersCouple()
                if player1._color == WHITE:
                    couple.current_player = player1
                else:
                    couple.current_player = player2
                player1._couple = couple
                player2._couple = couple
                cls._first_connected_player = None


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


class PlayerHandler(socketserver.StreamRequestHandler):
    _color = None
    _couple = None
    _opponent = None

    def handle(self):
        print(f'Connected: {self}')
        try:
            self._initialize()
            self._process_messages()
        except QuitMessageException:
            pass
        except Exception as e:
            print(e)
        print(f'Closed: {self}')

    def __str__(self):
        return f'{self.client_address} on {threading.current_thread().name}'

    def send(self, message):
        message = message.encode('utf-8')
        self.wfile.write(message)
        print(f'Sent {message}: {self}')

    def _initialize(self):
        PlayersCouple.join(self)
        if self._couple:
            self.send(color_message(self._color))
            self._opponent.send(color_message(self._opponent._color))

    def _process_messages(self):
        while True:
            message = self.rfile.read(10)
            if not message:
                break
            self._process_message(message)

    def _process_message(self, message):
        print(f'Received {message}: {self}')
        if self._is_message_valid(message):
            message = message.decode('utf-8')
            if message.startswith('QUIT'):
                self._opponent.send(message)
                raise QuitMessageException()
            elif self == self._couple.current_player:
                if message.startswith('ENDMOVE'):
                    self._couple.switch_current()
                self._opponent.send(message)
        else:
            raise ValueError(f'Invalid protocol message: {message}')

    @staticmethod
    def _is_message_valid(message):
        message = message.decode('utf-8')
        return (message.startswith('DIES') or
                message.startswith('MOVE') or
                message.startswith('ENDMOVE') or
                message.startswith('QUIT'))


def color_message(color):
    return f'COLOR {color}'.ljust(10, ' ')


host, port = sys.argv[1].split(':')
port = int(port)
with ThreadingTCPServer((host, port), PlayerHandler) as server:
    print('Backgammon server is running')
    server.serve_forever()