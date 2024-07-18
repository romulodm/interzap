from socket import *

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket(AF_INET, SOCK_STREAM)

    def start(self):
        self.client_socket.connect((self.host, self.port))
        print(f'Connected on: {self.host}:{self.port}')
        self.handle_messages()

    def close(self):
        self.client_socket.close()

    def handle_messages(self):
        while True:
            data = self.client_socket.recv(1024)
            print(f"Received {data!r}")

