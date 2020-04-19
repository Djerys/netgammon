import socket


class BGPClient:
    def __init__(self, host, port, timeout=0.1):
        self.host, self.port = host, port
        self.timeout = timeout
        self._socket = None

    @property
    def connected(self):
        return self._socket is not None

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.host, self.port))
        self._socket.settimeout(self.timeout)

    def disconnect(self):
        self._socket.close()
        self._socket = None

    def receive(self):
        try:
            message = self._socket.recv(32)
        except socket.timeout:
            raise BGPTimeoutError()
        message = message.decode('utf-8')
        formed_message = {'command': message[:(len(message.split()[0]))]}
        if message.startswith('DIES') or message.startswith('MOVE'):
            formed_message['args'] = tuple(int(i) for i in message[4:].split()[:2])
        elif message.startswith('COLOR'):
            formed_message['arg'] = message[5:].strip()
        return formed_message

    def send_dies(self, die1, die2):
        self._socket.send(f'DIES {die1} {die2}\n'.encode('utf-8'))

    def send_move(self, from_point, to_point):
        self._socket.send(f'MOVE {from_point} {to_point}\n'.encode('utf-8'))

    def send_endmove(self):
        self._socket.send('ENDMOVE\n'.encode('utf-8'))

    def send_quit(self):
        self._socket.send('QUIT\n'.encode('utf-8'))


class BGPTimeoutError(Exception):
    pass
