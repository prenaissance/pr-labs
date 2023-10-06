from dataclasses import dataclass
import json
import socket
import threading
from typing import Dict, List
HOST = '127.0.0.1'
PORT = 12345

@dataclass
class Client:
    socket: socket.socket
    name: str

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

rooms: Dict[str, List[socket.socket]] = []

def serve_connections():
    print(f"Server is listening on {HOST}:{PORT}")
    while True:
        client_socket, client_address = server_socket.accept()
        try:
            print(f"Accepted connection from {client_address}")
            connect_message_raw = client_socket.recv(2048).decode('utf-8')
            connect_message = json.loads(connect_message_raw)["payload"]
            room_name = connect_message["room"]
            client_name = connect_message["name"]
            client = Client(client_socket, client_name)
            if room_name not in rooms:
                rooms[room_name] = []
            rooms[room_name].append(client)

            receive_thread = threading.Thread(
                target=handle_client, args=(client, client_address, room_name))
            receive_thread.daemon = True
            receive_thread.start()
        except:
            client_socket.close()


def handle_client(client: Client, client_address, room_name: str):
    def remove_client():
        rooms[room_name].remove(client)
        client.socket.close()
        print(f"Client {client_address} disconnected")

    try:
        message = client.socket.recv(1024).decode('utf-8')
        if not message:
            remove_client()
            return

        print(f"Received from {client_address}: {message}")
        for client in rooms[room_name]:
            if client != client:
                client.socket.send(message.encode('utf-8'))
        handle_client(client, client_address, room_name)
    except:
        remove_client()


if __name__ == "__main__":
    serve_connections()
