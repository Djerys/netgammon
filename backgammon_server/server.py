import threading
import socketserver


HOST, PORT = 'localhost', 4567


WHITE = 'W'
RED = 'R'


class PlayersPair:
    _next_pair = None
    _selection_lock = threading.Lock()

    def __init__(self):
        self.current_player = None

    def switch_current(self):
        self.current_player = self.current_player.opponent

    @classmethod
    def join(cls, player):
        with cls._selection_lock:
            if cls._next_pair is None:
                cls._next_pair = PlayersPair()
                player.pair = cls._next_pair
                player.color = WHITE
            else:
                player.color = RED
                player.pair = cls._next_pair
                cls._next_pair = None


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


class PlayerHandler(socketserver.StreamRequestHandler):
    color = None
    pair = None
    opponent = None

    def handle(self):
        client = f'{self.client_address} on {threading.current_thread().name}'
        print(f'Connected: {client}')
        try:
            self.initialize()
            self.process_commands()
        except Exception as e:
            print(e)
        print(f'Closed: {client}')

    def initialize(self):
        PlayersPair.join(self)
        self.send(f'WELCOME {self.color}')
        if self.color == WHITE:
            self.pair.current_player = self
            self.send('Waiting wor opponent')
        else:
            self.opponent = self.pair.current_player
            self.opponent.opponent = self
            self.opponent.send('You start')

    def send(self, message):
        self.wfile.write(f'{message}\n'.encode('utf-8'))

    def process_commands(self):
        while True:
            command = self.rfile.readline()
            if not command:
                break
            command = command.decode('utf-8')
            print(command)


with ThreadingTCPServer((HOST, PORT), PlayerHandler) as server:
    print('Backgammon server is running')
    server.serve_forever()
