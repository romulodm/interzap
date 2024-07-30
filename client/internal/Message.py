class Message:
    def __init__(self, content, user):
        self.content = content
        self.sender = user
        self.delivered = None
        self.read = None

    def make_delivered(self):
        self.delivered = True

    def is_delivered(self):
        return self.delivered
    
    def make_read(self):
        self.read = True

    def is_read(self):
        return self.read
    
