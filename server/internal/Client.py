import threading

from server.utils.messages import Messages

class Client(threading.Thread):
    def __init__(self, conn, addr, server):
        super().__init__()
        self.connection = conn
        self.address = addr
        self.server = server
        self.online = True
        self.number = None
        self.messages = Messages()

    def run(self):
        self.connection.sendall(b'Welcome to Interzap! Please enter your number: ')
        self.number = self.connection.recv(1024).decode().strip()
        self.server.register_client(self.number, self)
        print(f'User {self.number} connected from {self.address}')
        
        while self.online:
            message = self.connection.recv(1024)
            if not message:
                break

            message = message.decode()
            print(f'Received message from {self.number}: {message}')
            recipient, msg = message.split(':', 1)
            self.server.send_message(recipient, f'{self.number}: {msg}')
        
        self.online = False
        self.server.unregister_client(self.number)
        self.connection.close()
        print(f'User {self.number} disconnected.')

    def send_message(self, message):
        self.connection.sendall(message.encode())
