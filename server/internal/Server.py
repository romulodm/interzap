from socket import *
from internal.Client import Client

class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 9070
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.clients = {}
        self.online_clients = {}

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f'Server running on: {self.host}:{self.port}')
        self.handle_connections()

    def close(self):
        self.server_socket.close()

    def handle_connections(self):
        while True:
            conn, addr = self.server_socket.accept()
            client = Client(conn, addr, self)
            client.start()

    def register_client(self, number, client):
        self.online_clients[number] = client

    def unregister_client(self, number):
        if number in self.online_clients:
            del self.online_clients[number]

    def send_message(self, number, message):
        if number in self.online_clients:
            self.online_clients[number].send_message(message)
        else:
            if number not in self.clients:
                self.clients[number] = Messages()
            self.clients[number].insert(message)
