from internal.queue import Queue

class User:
    def __init__(self, server, conn, addr):
        self.server = server # ChatServer instance, no typing to avoid circular import
        self.conn = conn
        self.addr = addr
        self.authenticated = False
        self.id = None
        self.online = False
        self.messages = Queue(self.server)

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
            self.server.register_user(self.addr, self.id, self)
            self.authenticated = True

            self.conn.sendall(f"02{self.id}".encode("utf-8"))
            return True

        elif code == "03":
            if self.authenticated:
                return False
            
            id = message[2:]
            if id in self.server.offline_users:
                try:
                    if self.server.login_user(self.addr, id, self):
                        self.id = message[2:]
                        self.authenticated = True
                        self.conn.sendall(f"04{message[2:]}".encode("utf-8"))
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
            
            self.server.send_message(sender_id, receiver_id, time, msg)

    def start(self):
        try:
            print(f'User connected with {self.addr} address! \n')
            
            self.server.register_unauthenticated_user(self, self.addr)
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
