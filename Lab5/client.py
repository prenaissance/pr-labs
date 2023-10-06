import json
import socket
import threading
# Server configuration
HOST = '127.0.0.1' # Server's IP address
PORT = 12345 # Server's port
# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Connect to the server
client_socket.connect((HOST, PORT))

def listen_for_messages():
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        print(f"Received: {message}")
    client_socket.close()
    
# Start a thread for listening for messages
listen_thread = threading.Thread(target=listen_for_messages)
listen_thread.daemon = True
listen_thread.start()

def main():
    print(f"Connected to {HOST}:{PORT}")
    name = input("Name: ")
    room_name = input("Room name: ")
    connect_message = {
        "type": "connect",
        "payload": {
            "name": name,
            "room_name": room_name
        }
    }
    client_socket.send(json.dumps(connect_message).encode("utf-8"))
    get_input()

def get_input():
    def close_client():
        client_socket.close()
        print("Disconnected from server")

    message = input()
    if message.lower() == 'exit':
        close_client()
        return
    
    client_socket.send(message.encode('utf-8'))
    get_input()

if __name__ == "__main__":
    main()