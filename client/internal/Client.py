class Client:
    def __init__(self, id, socket):
        self.id = id
        self.contacts = []

    def add_contact(self, user):
        if user.id != self.id:
            self.contacts.append(user)

    def remove_contact(self, user):
        self.contacts = [contact for contact in self.contacts if contact.id != user.id]
