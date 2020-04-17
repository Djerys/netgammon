import threading
import socketserver


HOST, PORT = 'localhost', 4567


class PlayersPair:
    _next_pair = None

    _selection_lock = threading.Lock()

    def __init__(self):
        self.current_player = None

    @classmethod
    def join(cls, player):
        with cls._selection_lock:
            if cls._next_pair is None:
                cls._next_pair = PlayersPair()
                player.pair = cls._next_pair
                player.color = 'W'
            else:
                player.color = 'R'
                player.pair = cls._next_pair
                cls._next_pair = None


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


class PlayerHandler(socketserver.StreamRequestHandler):
    def handle(self):
        client = f'{self.client_address} on {threading.current_thread().name}'
        print(f'Connected: {client}')
        while True:
            data = self.rfile.readline()
            if not data:
                break
            data = data.decode('utf-8')
            print(f'Received on {threading.current_thread().name}: {data}')


with ThreadingTCPServer((HOST, PORT), PlayerHandler) as server:
    print('Backgammon server is running')
    server.serve_forever()
