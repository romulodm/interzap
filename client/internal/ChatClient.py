from socket import *
import os
import json
import threading
import time

from internal.Client import Client
from util.convert_posix import convert_posix_to_hours

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client = None
        self.state = None
        self.alive = True
        self.selected_contact = None

    def close(self):
        self.alive = False
        self.client_socket.close()

    def handle_messages(self):
        while self.alive:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == "Welcome to Interzap!":
                    print(f"{message}\n")
                
                elif message[:2] == "02":
                    id = message[2:]
                    self.client = Client(id)
                    print(f"Authenticated with id: {id}\n")
                
                elif message[:2] == "04":
                    response = message[2:]
                    if response == "Error":
                        print("An error occurred with your login.")

                    else: 
                        self.client = Client(response)
                        print(f"Authenticated with id: {response}\n")              
                    
            except Exception as e:
                print(f"An error occurred on handler a message received: {e}")
                self.close()
                break

    def handle_auth(self):
        while self.alive and not self.client:
            message = input("You want login or register? ")

            if message == "1":
                self.client_socket.send(b'01')
                print("Processing your registration request...")
                time.sleep(0.5)
                return True

            elif message == "2":
                while self.alive:
                    id = input('Please enter your id (type "n" to cancel): ')
                    if id == "n" or id == "N":
                        print()
                        break
                    if len(id) == 13:
                        self.client_socket.send(f"03{id}".encode("utf-8"))
                        print("Processing your login request...")
                        time.sleep(0.5)
                        break
                    else: 
                        print("Invalid ID - must be have 13 digits.")

                return True

            else:
                print("Unknow command.")

    def handle_new_contact(self):
        print()
        while self.alive and self.client != None:
            contact_id = input('Enter the ID of the user you want to add or type "N" to cancel: Client-')

            if contact_id == "N" or contact_id == "n":
                print()
                self.state = None
                return True

            elif len(contact_id) != 6:
                print("ID must have 6 digits.")
            
            else:
                self.client.add_contact("Client-" + contact_id)

    def handle_list_contacts(self):
        print()
        while self.alive and self.client != None:
            print("Your contacts and groups:")
            if len(self.client.contacts) == 0:
                print("You have no contacts and/or groups added.\n")
                self.state = None
                break
            else:
                sorted_contacts = sorted(self.client.contacts)
                for i, contact in enumerate(sorted_contacts, start=1):
                    print(f"{i} - {contact}")

                choice = input('Which contact or group do you want to talk to? Enter the number or type "N" to cancel ')
                if str(choice) == "N" or choice == str("n"):
                    self.state = None
                    break

                elif 1 <= int(choice) <= len(sorted_contacts) and choice.isdigit():
                    self.selected_contact = sorted_contacts[int(choice) - 1]
                    self.display_chat()

                else:
                    print("Invalid choice, please enter a number corresponding to the contacts/groups listed.\n")

    def display_chat(self):
        while self.selected_contact:
            messages = self.client.get_messages_with_contact(self.selected_contact)
            for message in messages:
                print(f"[{convert_posix_to_hours(message['time'])}] {message['sender']}: {message['content']}\n")
            
            msg = input('Type your message here or type "N" to exit: ')
            if msg == "N" or msg == "n":
                self.state = "LIST_CONTACTS_AND_GROUPS"
                break
            elif len(msg) > 218:
                print("Your message is too long (max 218 characters).")
            else:
                self.client_socket.send(f"05{self.client.id}{self.selected_contact}{str(time.time())[:10]}{msg}".encode("utf-8"))
                self.client.add_message(self.client.id, self.selected_contact, msg)


    def handle_state(self):
        print("List of possibles commands:")
        print("1 - Add new contact")
        print("2 - Create new group")
        print("3 - List my contacts and groups to read and send messages")
        print("4 - Quit")
        while self.alive and self.client:
            message = input("What do you wanna do now on Interzap? ")

            if message == "1":
                self.state = "NEW_CONTACT"
                break

            if message == "2":
                self.state = "NEW_GROUP"
                break

            elif message == "3":
                self.state = "LIST_CONTACTS_AND_GROUPS"
                break

            elif message == "4":
                self.close()
                break

            else:
                print("Unknow command.")

    def handle_user_input(self):
        try:
            while self.alive:
                if not self.client:
                    print("You need to autenticate to enter on Interzap:\n")
                    print("Type 1 to register.\nor\nType 2 to login.")
                    self.handle_auth()
    
                elif self.client and self.state == None:
                    self.handle_state()

                elif self.client and self.state == "NEW_CONTACT":
                    self.handle_new_contact()

                elif self.client and self.state == "NEW_GROUP":
                    pass

                elif self.client and self.state == "LIST_CONTACTS_AND_GROUPS":
                    self.handle_list_contacts()

                
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.close()

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

