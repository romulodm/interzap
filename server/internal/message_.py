class Message:
    def __init__(self, code, sender_id, receiver_id, time, content):
        self.code = code
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.time = time
        self.content = content
        self.read = None
        self.delivered = None

    def make_delivered(self):
        self.delivered = True

    def is_delivered(self):
        return self.delivered
    
    def make_read(self):
        self.read = True

    def is_read(self):
        return self.read
    
