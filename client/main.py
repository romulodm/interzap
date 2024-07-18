from internal.ChatClient import ChatClient

HOST = "127.0.0.1"
PORT = 9070

if __name__ == "__main__":
    server = ChatClient(HOST, PORT)
    server.start()