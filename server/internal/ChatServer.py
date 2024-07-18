from socket import *
from internal.User import User
from messages import Messages

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.users = {}
        self.online_users = {}

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
            user = User(conn, addr, self)
            user.start()

    def register_user(self, number, user):
        self.online_users[number] = user

    def unregister_user(self, number):
        if number in self.online_users:
            del self.online_users[number]

    def send_message(self, number, message):
        if number in self.online_users:
            self.online_users[number].send_message(message)
        else:
            if number not in self.users:
                self.users[number] = Messages()
            self.users[number].insert(message)
