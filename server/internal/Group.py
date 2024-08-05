import time
from typing import List
from internal.user import User
from internal.message import Message

class Group:
    def __init__(self, server, users):
        self.server = server
        self.id = self.generate_group_id()
        self.creation = str(time.time())[:10]
        self.users: List[User] = users

    def generate_group_id(self):
        return f'Group-{self.server.groups_counter + 1:07d}'
    
    def send_message(self, message: Message):
        for user in self.users:
            if user.id in self.server.online_users:
                user.conn.sendall(f"12{message.sender_id}{self.id}{message.time}{message.content}".encode("utf-8"))
            else:
                user.messages.insert(message)
