import time

class User:
    def __init__(self, server, conn, addr):
        self.server = server # ChatServer instance, no typing to avoid circular import
        self.conn = conn
        self.addr = addr
        self.authenticated = False
        self.id = None
        self.online = False

    def set_id(self, id):
        self.id = id

    def set_conn(self, conn):
        self.conn = conn

    def set_addr(self, addr):
        self.addr = addr

    def generate_user_id(self):
        return f'Client-{self.server.users_counter + 1:06d}'
    
    def handle_messages(self, message):
        code = message[:2]
        if code == "01":
            if self.authenticated:
                return False
            
            self.id = self.generate_user_id()
            self.server.register_user(self.id, self)
            self.authenticated = True

            self.conn.sendall(f"02{self.id}".encode("utf-8"))
            return True

        elif code == "03":
            if self.authenticated:
                return False
            
            id = message[2:]
            if id in self.server.offline_users:
                try:
                    if self.server.login_user(id, self):
                        self.id = message[2:]
                        self.authenticated = True
                        self.conn.sendall(f"04{message[2:]}".encode("utf-8"))
                        
                        self.check_pending_messages()
                    else:
                        self.conn.sendall(f"04Error".encode("utf-8"))
                except Exception as e:
                    print("Error on login: ", e)
            else:
                self.conn.sendall(f"04Error".encode("utf-8"))

        elif code == "05":
            if not self.authenticated:
                return False
            
            # Here I divide each part of the message received based on the expected protocol
            sender_id, receiver_id, time, msg = message[2:15], message[15:28], message[28:38], message[38:]
            print("Message on server: ", sender_id, receiver_id, msg)
            if receiver_id[:5] == "Group":
                self.server.send_message_group(receiver_id, sender_id, time, msg)
            else:
                self.server.send_message(sender_id, receiver_id, time, msg)

        elif code == "08": # Message to confirm read
            if not self.authenticated:
                return False
            
            source_id, time = message[2:15], message[15:25]
            
            self.server.confirm_read(source_id, time, self.id)

        elif code == "10": # Message to creat a group
            id_creator, time = message[2:15], message[15:25]

            members_ids = []

            offset = 25
            member_length = 13
            max_members = 8

            # Extracting user ids from string
            while offset + member_length <= len(message) and len(members_ids) < max_members:
                member_id = message[offset:offset + member_length].strip()
                if member_id: 
                    members_ids.append(member_id)
                offset += member_length

            self.server.create_group(id_creator, time, members_ids)

    def check_pending_messages(self):
        pending_messages = self.server.load_pending_messages(self.id)

        # I put this sleep here because I need the client to be instantiated there on the client
        time.sleep(2) # I use a method called add_message or add_group_message on the client

        if pending_messages:
            for msg_tuple in pending_messages:
                msg = msg_tuple[0]
                self.conn.sendall(f'{msg}'.encode("utf-8"))
                time.sleep(.15)
            
            self.server.db.delete_pending_messages(self.id)

    def start(self):
        try:
            print(f'User connected with {self.addr} address! \n')
            self.conn.sendall(f'Welcome to Interzap!'.encode("utf-8"))
              
            self.online = True
            while self.online:
                message = self.conn.recv(1024)
                if not message:
                    break

                message = message.decode()
                self.handle_messages(message)
            
            self.online = False
            self.server.unregister_user(self.id)
            self.conn.close()
            print(f'User with {self.addr} has disconnected.')
        
        except ConnectionResetError:
            print(f"User with {self.addr} address has disconnected.")
            self.server.unregister_user(self.id)
            self.online = False
            self.authenticated = False
