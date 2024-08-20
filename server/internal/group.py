import time
from typing import List
from internal.user import User

class Group:
    def __init__(self, server, time, users, id=None):
        self.server = server
        self.id = id
        self.creation = time
        self.users = users

    def generate_group_id(self):
        return f'Group-{self.server.groups_counter + 1:07d}'
    
