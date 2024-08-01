import threading
from socket import *
from internal.User import User
from messages import Messages


class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.users = {}
        self.unauthenticated_users = {}

    def close(self):
        self.server_socket.close()
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f'Server running on: {self.host}:{self.port}')
        self.handle_connections()

    def handle_connections(self):
        while True:
            # Receives and accepts a new connection
            conn, addr = self.server_socket.accept()
            
            #Creates a User instance and a thread to validate received messages
            user = User(conn, addr, self)
            thread = threading.Thread(target=user.start)
            thread.start()

    def register_unauthenticated_user(self, addr, user):
        self.unauthenticated_users[addr] = user

    def register_user(self, addr, id, user):
        self.users[id] = user

        # Removing user from without authentication ones by your addr
        if addr in self.unauthenticated_users:
            del self.unauthenticated_users[addr]

    def unregister_user(self, id):
        if id in self.users:
            del self.users[id]

    def send_message(self, id, message):
        if id in self.users:
            self.users[id].conn.sendall(f'{message}'.encode('utf-8'))
        else:
            if id not in self.users:
                self.users[id].messages.insert(message)
            
