import socket


class BGPClient:
    def __init__(self, connection, timeout=0.001):
        self.connection = connection
        self.timeout = timeout
        self._socket = None

    @property
    def closed(self):
        return self._socket is None

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(self.connection)
        self._socket.settimeout(self.timeout)

    def close(self):
        self._socket.close()
        self._socket = None

    def receive(self):
        message = self._socket.recv(10)
        message = message.decode('utf-8')
        formed_message = {'command': message[:(len(message.split()[0]))]}
        if message.startswith('DIES') or message.startswith('MOVE'):
            formed_message['args'] = tuple(int(i) for i in message[4:].split()[:2])
        elif message.startswith('COLOR'):
            formed_message['arg'] = message[5:].strip()
        return formed_message

    def send_dies(self, die1, die2):
        message = f'DIES {die1} {die2}'.ljust(10, ' ')
        self._socket.send(message.encode('utf-8'))

    def send_move(self, from_point, to_point):
        message = f'MOVE {from_point} {to_point}'.ljust(10, ' ')
        self._socket.send(message.encode('utf-8'))

    def send_end_move(self):
        message = 'ENDMOVE'.ljust(10, ' ')
        self._socket.send(message.encode('utf-8'))

    def send_quit(self):
        message = 'QUIT'.ljust(10, ' ')
        self._socket.send(message.encode('utf-8'))
