import threading
from socket import *
from internal.User import User
from internal.Message import Message
from typing import Dict

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.users_counter = 0
        self.online_users: Dict[str, User] = {}
        self.offline_users: Dict[str, User] = {}
        self.unauthenticated_users: Dict[str, User] = {}

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
            user = User(self, conn, addr)
            thread = threading.Thread(target=user.start)
            thread.start()

    def register_unauthenticated_user(self, addr, user):
        self.unauthenticated_users[addr] = user

    def register_user(self, addr, id, user: User):
        print(id, addr, user)
        try:
            self.online_users[id] = user
            self.users_counter += 1

            # Removing user from without authentication ones by your addr
            if addr in self.unauthenticated_users:
                del self.unauthenticated_users[addr]

            # Making user not be offline
            if id in self.offline_users:
                del self.offline_users[id]

        except Exception as e:
            print("Error on register an user: ", e)

    def unregister_user(self, id):
        if id in self.online_users:
            user = self.online_users[id]
            del self.online_users[id]
            self.offline_users[id] = user

    def send_message(self, id_sender, id_receiver, time, message):
        if id_receiver in self.online_users:
            # If the user is online, send them a message
            self.online_users[id_receiver].conn.sendall(f"06{id_sender}{id_receiver}{time}{message}".encode("utf-8"))
        elif id_receiver in self.offline_users:
            # If the user is not online, I create a message with the content
            msg = Message(id_sender, id_receiver, time, message)
            # And add it to "messages" which is an instance of the Queue we created
            self.offline_users[id_receiver].messages.insert(msg)
        else:
            # If the user is not in the dictionaries, we warn that it does not exist (to sender)
            self.online_users[id_sender].conn.sendall(f"The user does not exist.".encode("utf-8"))



            
