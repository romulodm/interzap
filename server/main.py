from internal.chat_server import ChatServer
from internal.database import Database

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from host import HOST_IP

PORT = 9070

if HOST_IP != "":
    HOST_TO_USE = HOST_IP
else:
    HOST_TO_USE = "127.0.0.1"
    
if __name__ == "__main__":
    try:
        db = Database()
        db.start_db()
        
        server = ChatServer(HOST_TO_USE, PORT, db)
        server.start()
    except Exception as e:
        print("An error ocurred on main.py: ", e)