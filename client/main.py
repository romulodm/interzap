from internal.chat_client import ChatClient

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
    server = ChatClient(HOST_TO_USE, PORT)
    server.start()