from socket import *
import threading

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.user = None
        self.state = None

    def start(self):
        self.client_socket.connect((self.host, self.port))
        print(f'Connected on: {self.host}:{self.port}')
        print("""
    Connected on Interzap 1.0 © 2024
              
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠔⠒⣬⠉⠉⣍⡍⠁⢒⠢⠤⣀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡠⢔⢍⠀⠸⠤⣀⠡⢥⣤⣥⡥⠄⣁⡃⠠⠒⠉⠢⢄⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡠⢊⣠⡀⢈⢤⣢⣵⣾⣿⠟⠛⠛⠟⢿⣿⣾⣵⡢⡀⠎⢀⣑⢄⠀ 
⠀⠀⠀⠀⠀⡔⢅⡀⢁⢔⣵⣿⣿⣿⣿⠿⢶⠀⠀⢰⠳⢿⣿⣿⣿⣷⣕⡐⠘⠈⢢
⠀⠀⠀⠀⡜⠀⠀⠠⣳⣿⣿⣿⣿⠏⠀⣠⣼⠀⠀⢸⣤⠀⠉⢻⣿⣿⣿⣮⢆⢺⠧⢣
⠀⠀⠀⢰⠙⠤⢢⣳⣿⣿⣿⣿⠟⠀⠀⣀⣀⠀⠀⢀⣀⠂⠠⠙⠁⢹⣿⣿⣯⠆⢄⢀⡆
⠀⠀⠀⡆⠀⠀⡌⣿⣿⣿⠟⠁⢸⡀⠀⠈⢻⠀⠀⢸⣧⣀⣿⣶⣄⢸⣿⣿⣿⣼⠈⠁⢰⠀⠀⠀
⠀⠀⠀⡇⠚⠃⣿⣿⣟⠁⠀⠀⢾⣿⣦⣀⣸⠀⠀⢸⠉⠙⠻⣿⣿⣿⣿⣿⣿⣿⠘⠉⢸
⠀⠀⠀⠇⠀⠀⢃⣿⣿⣷⣄⠀⠈⡟⠉⠙⣿⠀⠀⢸⣄⡀⠀⠈⠿⠻⣿⣿⣿⢻⠀⠀⢸
⠀⠀⠀⠸⡀⠀⠘⡽⣿⣿⣿⡷⠜⠀⠀⡰⠛⠒⠒⠚⠛⢱⠀⠀⢸⣾⣿⣿⣟⠆⠀⠀⠇
⠀⠀⠀⠀⢣⠀⠀⠘⡽⣿⣿⣦⣤⡀⠈⠓⠶⠒⠒⢲⠶⠋⠀⣠⣿⣿⣿⢟⠎⠀⠀⡜⠀
⠀⠀⠀⠀⠀⠣⡀⠀⠈⠪⡻⣿⣿⣿⣷⣦⣤⠀⠀⢸⣤⣴⣾⣿⣿⣿⠋⠁⠀⢀⠜⠀
⠀⠀⠀⠀⠀⠀⠑⢄⠀⠀⠈⠚⠝⡻⢿⣿⣤⣤⣠⣤⣴⡿⢿⡻⠑⠁⠀⠀⡠⠊⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠑⠢⣀⠀⠀⠀⡍⠐⢚⡛⢛⣓⠂⡭⡄⠀⠀⣀⠔⠊⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⠨⠥⢀⣈⣃⣈⣚⣀⠤⠅⠒⠉⠀⠀ 

""")
        receive_thread = threading.Thread(target=self.handle_messages)
        receive_thread.start()

        self.handle_user_input()

    def close(self):
        self.client_socket.close()

    def handle_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if data:
                    print(data.decode('utf-8'))
                else:
                    print("Connection closed by the server.")
                    break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    def handle_auth(self):
        while True:
            message = input("You want login or register? ")

            if message == "1":
                self.client_socket.send(f"01")
                print("Processing your registration request...")
                return True

            elif message == "2":
                while True:
                    id = input("Please enter your id: ")
                    if len(id) == 13 :
                        break
                    else: 
                        print("Invalid ID - must be have 13 digits.")

                self.client_socket.send(f"03{id}")
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

            elif message == "2":
                self.state == "LIST_CONTACTS"
                break

            elif message == "3":
                self.close()
                break

            else:
                print("Unknow command.")


    def handle_user_input(self):
        try:
            while True:
                if not self.user:
                    print("You need to autenticate to enter on Interzap:\n")
                    print("Type 1 to register.\nor\nType 2 to login.")
                    auth = self.handle_auth()
                    if auth:
                        print("Message sended to server. Waiting for response...")

                elif self.user and self.state == None:
                    print("What do you wanna do now on Interzap?")
                    print("1 - Add new contact")
                    print("2 - List my contacts to read and send messages")
                    print("3 - Quit")
                    self.handle_auth()

                elif self.user and self.state == "NEW_CONTACT":
                    pass

                elif self.user and self.state == "LIST_CONTACTS":
                    pass

                
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.close()


