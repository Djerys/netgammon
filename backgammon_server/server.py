import threading
import socketserver


HOST, PORT = 'localhost', 4567


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


class BackgammonHandler(socketserver.StreamRequestHandler):
    def handle(self):
        client = f'{self.client_address} on {threading.current_thread().name}'
        print(f'Connected: {client}')
        while True:
            data = self.rfile.readline()
            if not data:
                break
            data = data.decode('utf-8')
            print(f'Received on {threading.current_thread().name}: {data}')


with ThreadingTCPServer((HOST, PORT), BackgammonHandler) as server:
    print('Backgammon server is running')
    server.serve_forever()
