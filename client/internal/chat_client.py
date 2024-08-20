from socket import *
import keyboard
import threading
import time as t

from internal.client import Client
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
        self.last_message_received = None
        self.check_message = False # Variable to control the running state of the check_message thread on chat

    def close(self):
        self.alive = False
        self.client_socket.close()

    def handle_messages(self):
        while self.alive:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == "Welcome to Interzap!":
                    print(f"{message}\n")
                
                elif message[:2] == "02": # his message indicates that I was able to register
                    id = message[2:]
                    self.client = Client(id)
                    print(f"Authenticated with id: {id}\n")
                
                elif message[:2] == "04": # This message i created to confirm login and authenticate a user (overengineering)
                    response = message[2:]
                    if response == "Error":
                        print("An error occurred with your login.")

                    else: 
                        self.client = Client(response)
                        print(f"Authenticated with id: {response}\n")       

                elif message[:2] == "06": # I received a message

                    # Here I divide each part of the message received based on the expected protocol
                    sender_id, receiver_id, time, msg = message[2:15], message[15:28], message[28:38], message[38:]

                    if receiver_id[:5] == "Group":
                        self.last_message_received = receiver_id
                        self.client.add_group_message(sender_id, receiver_id, msg, time)
                        
                    else:
                        self.last_message_received = sender_id
                        self.client.add_message(sender_id, receiver_id, msg, time)

                elif message[:2] == "07": # Message delivered

                    # Here I divide each part of the message received based on the expected protocol
                    receiver_id, time = message[2:15], message[15:25]
                    self.client.make_message_delivered(receiver_id, time)

                elif message[:2] == "09": # Message read

                    # Here I divide each part of the message received based on the expected protocol
                    receiver_id, time = message[2:15], message[15:25]
                    self.client.make_message_read(receiver_id, time)

                elif message[:2] == "11": # I'm a part of group now

                    # Parse the group creation message
                    group_id = message[2:15]

                    # He i add the group to contacts
                    self.client.add_contact(group_id)
                            
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
                t.sleep(0.5)
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
                        t.sleep(0.5)
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

                choice = input('Which contact or group do you want to talk to? Enter the number or type "C" to cancel: ')
                if str(choice) == "C" or choice == str("c"):
                    self.state = None
                    print()
                    break

                elif any(char.isalpha() for char in choice):
                    print("Your choice contains letters, choose a contact with numbers.\n")

                elif 1 <= int(choice) <= len(sorted_contacts) and choice.isdigit():
                    self.selected_contact = sorted_contacts[int(choice) - 1]
                    self.chat()

                else:
                    print("Invalid choice, please enter a number corresponding to the contacts/groups listed.\n")

    def handle_new_group(self):
        try:
            print()
            if not self.client.contacts:
                print("You have no contacts to add to a group.")

            sorted_contacts = sorted(self.client.contacts)
            non_group_contacts = [contact for contact in sorted_contacts if not contact.startswith("Group-")]

            print("Your contacts:")

            if not non_group_contacts:
                print("You have no individual contacts to add to a group.")
                return
            
            for i, contact in enumerate(non_group_contacts, start=1):
                print(f"{i} - {contact}")

            group_contacts = []

            while len(group_contacts) < 8:
                choice = input('Enter the number of the contact you want to add to the group, or type "D" when done: ')

                if choice.lower() == "d":
                    self.state = None
                    print()
                    break

                elif any(char.isalpha() for char in choice) or not choice.isdigit():
                    print("Invalid input, please enter a valid number corresponding to the contacts listed.\n")
                    continue

                index = int(choice) - 1

                if index < 0 or index >= len(non_group_contacts):
                    print("Invalid choice, please enter a number corresponding to the contacts listed.\n")
                    continue

                selected_contact = non_group_contacts[index]

                if selected_contact in group_contacts:
                    print(f"{selected_contact} is already in the group.\n")
                else:
                    group_contacts.append(selected_contact)
                    print(f"{selected_contact} added to the group.\n")

                if len(group_contacts) == 8:
                    print("Maximum number of contacts (8) reached.\n")
                    break

            if group_contacts:
                str_members = ""
                for id in group_contacts:
                    str_members += id
                
                self.client_socket.sendall(f"10{self.client.id}{str(t.time())[:10]}{str_members}".encode("utf-8"))
            else:
                print("No group created.")
        
        except Exception as e:
            print("An error ocurred on handle_new_group method: ", e)

    def chat(self):
        try:
            self.display_messages()
            print('Press "SHIFT" to type a new message or press "ESC" to exit.')

            while self.selected_contact:
                if keyboard.is_pressed('escape'):
                    self.state = "LIST_CONTACTS_AND_GROUPS"
                    self.selected_contact = None
                    break
                
                if keyboard.is_pressed('shift'):
                    msg = input('Type your message or type "C" to cancel: ')
                    if len(msg) > 218:
                        print("Your message is too long (max 218 characters).")
                        print('Press "SHIFT" to type a new message or press "ESC" to exit.')
                        
                    elif msg != "C" and msg != "c":
                        self.client_socket.sendall(f"05{self.client.id}{self.selected_contact}{str(t.time())[:10]}{msg}".encode("utf-8"))
                        
                        if self.selected_contact[:5] == "Group":
                            self.client.add_group_message(self.client.id, self.selected_contact, msg)
                        else:
                            self.client.add_message(self.client.id, self.selected_contact, msg)

                        self.display_messages()
                        print('Press "SHIFT" to type a new message or press "ESC" to exit.')
                    
                    else:
                        print('Press "SHIFT" to type a new message or press "ESC" to exit.')

                    t.sleep(.1)
                
                # Checking for new messages using self.last_message_received
                if self.selected_contact and self.last_message_received == self.selected_contact:
                    self.last_message_received = None
                    keyboard.clear_all_hotkeys()     
                    self.display_messages() 
                    print('Press "SHIFT" to type a new message or press "ESC" to exit.') 
                
                t.sleep(.1)

        except Exception as e:
            print("An error ocurred on chat: ", e)
            self.selected_contact = None
    
    def display_messages(self):
        try:
            print(f"\nYour messages with {self.selected_contact} user:\n")
            messages = self.client.get_messages_with_contact(self.selected_contact)
            for message in messages:
                print(f"[{convert_posix_to_hours(message['time'])}] {message['sender']}: {message['content']}")
                
                # Checking here why group messages don't have 'delivered' and 'read'
                if self.selected_contact[:5] != "Group":
                    if message['delivered'] == True and message['read'] == True:
                        print('✓✓✓\n')
                    elif  message['delivered'] == True and message['read'] == False:
                        print('✓✓\n')
                    else:
                        print('✓\n')
                else:
                    print('✓\n')

        except Exception as e:
            print("An error ocurred on display_messages method on chat_client: ", e)

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
                    self.handle_new_group()

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
            
            t.sleep(0.5)
            self.handle_user_input()
        
        except Exception as e:
            print(f"An error occurred when trying to connect to the server: {e}")

