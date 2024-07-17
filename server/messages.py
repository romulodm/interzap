class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class Messages:
    def __init__(self):
        self.ini = None
        self.last = None
        self.size = 0

    def empty(self):
        return self.size == 0
    
    def get(self):
        if not self.empty():
            return self.ini.data
        
    def remove(self):
        if not self.empty():
            self.ini = self.ini.next
            self.size -= 1
            if self.empty():
                self.last = None

    def insert(self, data):
        new_message = Node(data)
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
