from dataclasses import dataclass
import socket
import threading
from typing import Callable, Dict, List

from common import Message
HOST = '127.0.0.1'
PORT = 12345


@dataclass
class Client:
    socket: socket.socket
    name: str
    room: str


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

rooms: Dict[str, List[Client]] = {}

running = True

ctrlc_thread = threading.Thread(target=lambda: input() == "exit")

message_handlers: Dict[str, Callable[[Client, dict], None]] = {
    "message": lambda client, payload: broadcast(
        Message("message", {"sender": client.name, "text": payload["text"]}), client.room, client),
}

def handle_message(client: Client, message: Message):
    message_type = message.type
    print(f"Received message from {client.name}")
    handler = message_handlers[message_type]
    if not handler:
        print(f"Unknown message type '{message_type}'")
        return
    handler(client, message.payload)

def remove_client(client: Client, client_address: str, room_name: str):
    rooms[room_name].remove(client)
    client.socket.close()
    print(f"Client {client_address} disconnected")

def send_response(client: Client, message: Message):
    print(f"Sending response to {client.name}")
    print(message.to_json())
    client.socket.send(message.to_json().encode('utf-8'))


def broadcast(message: Message, room_name: str, sender: Client = None):
    print(f"Broadcasting message to {room_name}")
    print(message.to_json())
    encoded_message = message.to_json().encode('utf-8')
    for client in filter(lambda x: x != sender, rooms[room_name]):
        client.socket.send(encoded_message)


def serve_connections():
    print(f"Server is listening on {HOST}:{PORT}")
    while True:
        client_socket, client_address = server_socket.accept()
        try:
            print(f"Accepted connection from {client_address}")
            connect_message_raw = client_socket.recv(2048).decode('utf-8')
            connect_message_payload = Message.from_json(
                connect_message_raw).payload

            room_name = connect_message_payload["room"]
            client_name = connect_message_payload["name"]

            client = Client(client_socket, client_name, room_name)
            register_client(client, client_address)
        except KeyboardInterrupt:
            print("Closing server")
            break
        except Exception:
            remove_client(client, client_address, room_name)


def register_client(client: Client, client_address: str):
    room_name = client.room
    if room_name not in rooms:
        rooms[room_name] = []
    rooms[room_name].append(client)

    acknowledge_message = Message(
        "acknowledge", {"message": f"Welcome to {room_name}, {client.name}!"})
    send_response(client, acknowledge_message)

    receive_thread = threading.Thread(
        target=handle_client, args=(client, client_address))
    receive_thread.daemon = True
    receive_thread.start()

    connection_notification = Message(
        "notification", {"message": f"{client.name} has joined the room"})
    broadcast(connection_notification, room_name, client)


def handle_client(client: Client, client_address):
    while True:
        try:
            raw_message = client.socket.recv(1024).decode('utf-8')
            print(f"Received message from {client.name}:")
            print(raw_message)
            if not raw_message:
                continue

            received_message = Message.from_json(raw_message)
            handle_message(client, received_message)
        except Exception as e:
            print(f"Error from client {client.name}: {e}")


if __name__ == "__main__":
    serve_connections()
