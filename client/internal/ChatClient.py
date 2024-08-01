from socket import *
import threading
import time
from internal.Client import Client

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client = None
        self.state = None

    def start(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f'Connected on: {self.host}:{self.port}')
            print("""
Connected on Interzap 1.0 © 2024
              
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠔⠒⣬⠉⠉⣍⡍⠁⢒⠢⠤⣀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡠⢔⢍⠀⠸⠤⣀⠡⢥⣤⣥⡥⠄⣁⡃⠠⠒⠉⠢⢄⠀⠀⠀
⠀⠀⠀⠀⡠⢊⣠⡀⢈⢤⣢⣵⣾⣿⠟⠛⠛⠟⢿⣿⣾⣵⡢⡀⠎⢀⣑⢄⠀ 
⠀⠀⠀⡔⢅⡀⢁⢔⣵⣿⣿⣿⣿⠿⢶⠀⠀⢰⠳⢿⣿⣿⣿⣷⣕⡐⠘⠈⢢
⠀⠀⡜⠀⠀⠠⣳⣿⣿⣿⣿⠏⠀⣠⣼⠀⠀⢸⣤⠀⠉⢻⣿⣿⣿⣮⢆⢺⠧⢣
⠀⢰⠙⠤⢢⣳⣿⣿⣿⣿⠟⠀⠀⣀⣀⠀⠀⢀⣀⠂⠠⠙⠁⢹⣿⣿⣯⠆⢄⢀⡆
⠀⡆⠀⠀⡌⣿⣿⣿⠟⠁⢸⡀⠀⠈⢻⠀⠀⢸⣧⣀⣿⣶⣄⢸⣿⣿⣿⣼⠈⠁⢰⠀⠀⠀
⠀⡇⠚⠃⣿⣿⣟⠁⠀⠀⢾⣿⣦⣀⣸⠀⠀⢸⠉⠙⠻⣿⣿⣿⣿⣿⣿⣿⠘⠉⢸
⠀⠇⠀⠀⢃⣿⣿⣷⣄⠀⠈⡟⠉⠙⣿⠀⠀⢸⣄⡀⠀⠈⠿⠻⣿⣿⣿⢻⠀⠀⢸
⠀⠸⡀⠀⠘⡽⣿⣿⣿⡷⠜⠀⠀⡰⠛⠒⠒⠚⠛⢱⠀⠀⢸⣾⣿⣿⣟⠆⠀⠀⠇
⠀⠀⢣⠀⠀⠘⡽⣿⣿⣦⣤⡀⠈⠓⠶⠒⠒⢲⠶⠋⠀⣠⣿⣿⣿⢟⠎⠀⠀⡜⠀
⠀⠀⠀⠣⡀⠀⠈⠪⡻⣿⣿⣿⣷⣦⣤⠀⠀⢸⣤⣴⣾⣿⣿⣿⠋⠁⠀⢀⠜⠀
⠀⠀⠀⠀⠑⢄⠀⠀⠈⠚⠝⡻⢿⣿⣤⣤⣠⣤⣴⡿⢿⡻⠑⠁⠀⠀⡠⠊⠀
⠀⠀⠀⠀⠀⠀⠑⠢⣀⠀⠀⠀⡍⠐⢚⡛⢛⣓⠂⡭⡄⠀⠀⣀⠔⠊⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⠨⠥⢀⣈⣃⣈⣚⣀⠤⠅⠒⠉⠀⠀ 

""")
            receive_thread = threading.Thread(target=self.handle_messages)
            receive_thread.start()
            
            time.sleep(0.5)
            self.handle_user_input()
        
        except Exception as e:
            print(f"An error occurred when trying to connect to the server: {e}")

    def close(self):
        self.client_socket.close()

    def handle_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == "Welcome to Interzap!":
                    print(f"{message}\n")
                
                elif message[:2] == "02":
                    id = message[2:]
                    self.client = Client(id, self.client_socket)
                    print(f"Authenticated with id: {id}\n")
                
                elif message[:2] == "04":
                    response = message[2:]
                    if response == "Error":
                        print("An error occurred with your login.")
                    else: 
                        self.client = Client(id, self.client_socket)
                        print(f"Authenticated with id: {id}\n")              
                    
            except Exception as e:
                print(f"An error occurred on handler a message received: {e}")
                break

    def handle_auth(self):
        while True:
            message = input("You want login or register? ")

            if message == "1":
                self.client_socket.send(b'01')
                print("Processing your registration request...")
                return True

            elif message == "2":
                while True:
                    id = input("Please enter your id: ")
                    if len(id) == 13 :
                        break
                    else: 
                        print("Invalid ID - must be have 13 digits.")

                self.client_socket.send(f"03{id}".encode("utf-8"))
                print("Processing your login request...")
                return True

            else:
                print("Unknow command.")

    def handle_state(self):
        while True:
            message = input("What do you wanna do? ")

            if message == "1":
                self.state == "NEW_CONTACT"
                break

            if message == "2":
                self.state == "NEW_GROUP"
                break

            elif message == "3":
                self.state == "LIST_CONTACTS_AND_GROUPS"
                break

            elif message == "4":
                self.close()
                break

            else:
                print("Unknow command.")


    def handle_user_input(self):
        try:
            while True:
                if not self.client:
                    print("You need to autenticate to enter on Interzap:\n")
                    print("Type 1 to register.\nor\nType 2 to login.")
                    self.handle_auth()
    
                elif self.client and self.state == None:
                    print("What do you wanna do now on Interzap?")
                    print("1 - Add new contact")
                    print("2 - Create new group")
                    print("3 - List my contacts and groups to read and send messages")
                    print("4 - Quit")
                    self.handle_auth()

                elif self.client and self.state == "NEW_CONTACT":
                    pass

                elif self.client and self.state == "NEW_GROUP":
                    pass

                elif self.client and self.state == "LIST_CONTACTS_AND_GROUPS":
                    pass

                
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.close()


