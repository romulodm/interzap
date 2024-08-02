import threading
import time
from socket import *
from typing import Dict
from internal.User import User
from internal.Message import Message
from internal.Group import Group

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.users_counter = 0
        self.online_users: Dict[str, User] = {}
        self.offline_users: Dict[str, User] = {}
        self.unauthenticated_users: Dict[str, User] = {}
        self.groups: Dict[str, Group] = {}
        self.groups_counter = 0

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
        self.confirm_receipt(id_sender)

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

    def confirm_receipt(self, id_sender):
        if id_sender in self.online_users:
            self.online_users[id_sender].conn.sendall(f"Message arrived on the server!")

    def confirm_delivery(self, id_sender, id_receiver, time):
        if id_sender in self.online_users:
            self.online_users[id_sender].conn.sendall(f"07{id_receiver}{str(time.time())[:10]}")

    def confirm_read(self, id_sender, id_receiver, time):
        if id_sender in self.online_users:
            self.online_users[id_sender].conn.sendall(f"08{id_receiver}{str(time.time())[:10]}")

    def create_group(self, id_creator, time, members):
        group = Group(id_creator, time, members)
        self.groups[group.id] = group
        for member_id in members:
            if member_id in self.online_users:
                self.online_users[member_id].conn.sendall(f"11{group.id}{group.creation}{str(time.time())[:10]}{members}".encode("utf-8"))
        
        if id_creator in self.online_users:
            self.online_users[id_creator].conn.sendall(f"11{group.id}{group.creation}{str(time.time())[:10]}{members}".encode("utf-8"))




            
