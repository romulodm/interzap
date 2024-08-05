from server.internal.chat_server import ChatServer
from internal.database import Database

HOST = "127.0.0.1"
PORT = 9070

if __name__ == "__main__":
    try:
        db = Database()
        db.start_db()
        
        server = ChatServer(HOST, PORT, db)
        server.start()
    except Exception as e:
        print("An error ocurred on main.py: ", e)