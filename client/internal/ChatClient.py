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

            if message == "2":
                name = input("Please enter your name: ")
                self.client_socket.send(f"01{name}")
                return True

            elif message == "1":
                while True:
                    credentials = input("Please enter your id and name (separated by space): ")
                    parts = credentials.split()
                    if len(parts) != 2:
                        print("Unknown command.")
                    
                    id, name = parts

                    try:
                        id = int(id)
                        if len(id) == 13 :
                            break
                        else: 
                            print("Invalid ID (must be have 13 digits).")
                    except ValueError:
                        print("Invalid ID.")

                self.client_socket.send(f"03{id}{name}")
                return True

            else:
                print("Unknow command.")


    def handle_user_input(self):
        try:
            while True:
                if not self.user:
                    print("You need to autenticate to enter on Interzap:\n")
                    print("Type 1 to login.\nor\nType 2 to register.")
                    auth = self.handle_auth()
                    if auth:
                        print("Message sended to server. Waiting for response...")

                elif self.user and self.state == None:
                    print("What do you wanna do now on Interzap?")
                    print("1 - Add new contact")
                    print("2 - List my contacts to read and send messages")
                    print("3 - Quit")
                    


                message = input()
                self.client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.close()


