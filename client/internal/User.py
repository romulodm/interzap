class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.contacts = []

    def add_contact(self, user):
        if user.id != self.id:
            self.contacts.append(user)

    def remove_contact(self, user):
        self.contacts = [contact for contact in self.contacts if contact.id != user.id]
