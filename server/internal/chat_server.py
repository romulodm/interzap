import threading
import time
from socket import *
from typing import Dict
from internal.user import User
from internal.group import Group
from internal.database import Database

class ChatServer:
    def __init__(self, host, port, db: Database):
        self.host = host
        self.port = port
        self.db = db
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.users_counter = 0
        self.online_users: Dict[str, User] = {}
        self.offline_users: Dict[str, User] = {}
        self.groups: Dict[str, Group] = {}
        self.groups_counter = 0

    def close(self):
        self.server_socket.close()

    def increasing_groups_counter(self):
        self.groups_counter += 1

    def load_users_from_db(self):
        # Load all users from the database
        users = self.db.get_all_users()

        self.users_counter = len(users)
        for user in users:
            user_id = user[0]
            # Create user instances and place them in sefl.offline_users
            self.offline_users[user_id] = User(self, None, None)
            self.offline_users[user_id].id = user_id
            self.offline_users[user_id].messages = []

    def load_groups_from_db(self):
        # Load all groups from the database
        groups = self.db.get_all_groups()

        self.groups_counter = len(groups)
        for group in groups:
            group_id = group[0]
            # Create groups intances and place them in self.groups
            members = self.db.get_group_members(group_id)
            member_ids = [member[0] for member in members]
            self.groups[group_id] = Group(self, None, member_ids, group_id)

    def load_pending_messages(self, id):
        return self.db.get_pending_messages(id)
 
    def start(self):
        try:
            self.load_users_from_db()
            self.load_groups_from_db()
        
        except Exception as e:
            print("An error ocurred on load database: ", e)

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f'Server running on: {self.host}:{self.port}')
        self.handle_connections()

    def handle_connections(self):
        while True:
            # Receives and accepts a new connection
            conn, addr = self.server_socket.accept()
            
            # Creates a User instance and a thread to validate received messages
            user = User(self, conn, addr)
            thread = threading.Thread(target=user.start)
            thread.start()

    def register_user(self, id, user: User):
        try:
            self.online_users[id] = user
            self.users_counter += 1
            user.id = id

            # Adding user on DB
            self.db.create_user(id)

        except Exception as e:
            print("Error on register an user: ", e)

    def login_user(self, id, user: User):
        try:
            # Check if user exists and making user not be offline
            if id in self.offline_users:
                self.online_users[id] = user
                del self.offline_users[id]
                user.id = id 
                
                return True
            return False
        
        except Exception as e:
            print("Error on login an user: ", e)
            return False

    def unregister_user(self, id):
        if id in self.online_users:
            user = self.online_users[id]
            del self.online_users[id]
            self.offline_users[id] = user
    
    def send_message_group(self, id_group, id_sender, time, message):
        if id_group in self.groups:
            for member_id in self.groups[id_group].users:
                
                if member_id in self.online_users:
                    
                    # Checking here to not have a repeated message in the client who sent the message
                    if id_sender != member_id:
                        self.online_users[member_id].conn.sendall(f"06{id_sender}{id_group}{time}{message}".encode("utf-8"))
                
                elif member_id in self.offline_users:
                    # Inserting the message on "pending messages" table on SQLite
                    self.db.add_pending_message(member_id, f"06{id_sender}{id_group}{time}{message}", int(time))

                else:
                    # If the user is not in the dictionaries, we warn that
                    print(f"Error on send_group_message -> the user {member_id} does not exist.")

    def send_message(self, id_sender, id_receiver, time, message): 
        if id_receiver in self.online_users:
            # If the user is online, send them a message
            try:
                error = self.online_users[id_receiver].conn.sendall(f"06{id_sender}{id_receiver}{time}{message}".encode("utf-8"))
                
                # With sendall method: None is returned on success
                if error == None:
                    # So if the message was sent, I confirm delivery to the sender
                    self.send_confirm_delivered(id_sender, id_receiver, time)

            except Exception as e:
                print("An error ocurred on send message.")

        elif id_receiver in self.offline_users:
            # Inserting the message on "pending messages" table on SQLite
            self.db.add_pending_message(id_receiver, f"06{id_sender}{id_receiver}{time}{message}", int(time))

        else:
            # If the user is not in the dictionaries, we warn that
            print(f"Error on send_message -> the user {id_receiver} does not exist.")

    def send_confirm_delivered(self, id_sender, id_receiver, time):
        if id_sender in self.online_users:
            self.online_users[id_sender].conn.sendall(f"07{id_receiver}{time}".encode("utf-8"))
        elif id_sender in self.offline_users:
            self.db.add_pending_message(id_sender, f"07{id_receiver}{time}", time)
        else:
            print(f"Error on send_confirm_delivered, user {id_sender} does not exists.")

    def confirm_read(self, id_source, time, id_receiver):
        try: 
            if id_source in self.online_users:
                self.online_users[id_source].conn.sendall(f"09{id_receiver}{time}".encode("utf-8"))
            elif id_source in self.offline_users:
                self.db.add_pending_message(id_source, f"09{id_receiver}{time}", int(time))
            else:
                print(f"Problem in confirm_read method, user {id_source} does not exists.")
        
        except Exception as e:
            print("An error ocurred on confirm_read method: ", e)

    def create_group(self, id_creator, time, members):
        members.append(id_creator)

        group = Group(self, time, members)
        group.generate_group_id()

        self.db.create_group(group.id)
        self.groups[group.id] = group

        for member_id in members:
            self.db.add_user_to_group(member_id, group.id)
                    
        str_members = ""
        for member_id in members:
            str_members += member_id

        for member_id in members:
            if member_id != id_creator:
                if member_id in self.online_users:
                    self.online_users[member_id].conn.sendall(f"11{group.id}{time}{str_members}".encode("utf-8"))
                else:
                    # Inserting the message on "pending messages" table on SQLite
                    self.db.add_pending_message(member_id, f"11{group.id}{time}{str_members}", int(time))

        if id_creator in self.online_users:
            self.online_users[id_creator].conn.sendall(f"11{group.id}{time}{members}".encode("utf-8"))
  
