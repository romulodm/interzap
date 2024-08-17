import json
import os
import time

class Client:
    def __init__(self, id):
        self.id = id
        self.contacts = []
        self.messages = {}
        self.load_data_from_file()

    def add_contact(self, id):
        if id not in self.contacts:
            self.contacts.append(id)
            self.save_data_to_file()
            print("Contact added.")
        else:
            print("You have already added this contact.")

    def remove_contact(self, id):
        if id in self.contacts:
            self.contacts.remove(id)
            self.save_data_to_file()
            print("Contact removed.")
        else:
            print("Contact does not exist.")

    def add_message(self, sender_id, receiver_id, content, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())
        
        message_data = {
            'sender': sender_id,
            'time': timestamp,
            'content': content
        }

        if sender_id == self.id:
            if receiver_id not in self.messages:
                self.messages[receiver_id] = []
            self.messages[receiver_id].append(message_data)
            self.messages[receiver_id].sort(key=lambda x: x['time'])
        
        if receiver_id == self.id:
            if sender_id not in self.messages:
                self.messages[sender_id] = []
            self.messages[sender_id].append(message_data)
            self.messages[sender_id].sort(key=lambda x: x['time'])

        self.save_data_to_file()

    def save_data_to_file(self):
        filename = f"client/backups/{self.id}.json"
        data = {
            'contacts': self.contacts,
            'messages': self.messages
        }
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    def load_data_from_file(self):
        filename = f"client/backups/{self.id}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                data = json.load(file)
                self.contacts = data.get('contacts', [])
                self.messages = data.get('messages', {})
        else:
            self.contacts = []
            self.messages = {}
            
    def get_messages_with_contact(self, client_id):
        return self.messages.get(client_id, [])
