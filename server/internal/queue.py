from internal.message import Message

class Node:
    def __init__(self, message):
        self.message: Message = message
        self.next = None

class Queue:
    def __init__(self, server):
        self.server = server
        self.ini = None
        self.last = None
        self.size = 0

    def empty(self):
        return self.size == 0
    
    def get(self):
        if not self.empty():
            return self.ini.message
        
    def remove(self):
        if not self.empty():
            self.ini = self.ini.next
            self.size -= 1
            if self.empty():
                self.last = None

    def insert(self, message: Message):
        new_message = Node(message)
        if self.empty():
            self.ini = new_message
            self.last = new_message
        else:
            self.last.next = new_message
            self.last = new_message
        self.size += 1

    def destroy(self):
        while not self.empty():
            self.remove()
