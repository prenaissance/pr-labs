from dataclasses import dataclass
from os import makedirs, path
import socket
import threading
from typing import Callable, Dict, List
import base64

from common import Message
HOST = '127.0.0.1'
PORT = 12345
MEDIA_PATH = ".\server_media"


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


def handle_upload(client: Client, payload: dict):
    try:
        file_name: str = payload["file_name"]
        file_path = path.join(MEDIA_PATH, file_name)
        if not path.exists(path.dirname(file_path)):
            makedirs(path.dirname(file_path))
        base64_data: str = payload["data"]
        data = base64.b64decode(base64_data)
        with open(file_path, "wb") as file:
            file.write(data)
        send_response(client, Message("acknowledge", {
                      "message": "File uploaded successfully"}))
        broadcast(Message("notification", {
            "message": f"{client.name} uploaded {file_name}"}), client.room, client)
    except Exception as e:
        send_response(client, Message(
            "notification", {"message": f"Error: {e}"}))


def handle_download(client: Client, payload: dict):
    try:
        file_name: str = payload["file_name"]
        file_path = path.join(MEDIA_PATH, file_name)
        if (not path.exists(file_path)):
            send_response(client, Message("notification", {
                          "message": f"File {file_name} does not exist"}))
            return
        with open(file_path, "rb") as file:
            data = file.read()
        base64_data: str = base64.b64encode(data).decode("utf-8")
        send_response(client, Message(
            "download", {"file_name": file_name, "data": base64_data}))
    except Exception as e:
        send_response(client, Message(
            "notification", {"message": f"Error: {e}"}))


message_handlers: Dict[str, Callable[[Client, dict], None]] = {
    "message": lambda client, payload: broadcast(
        Message("message", {"sender": client.name, "text": payload["text"]}), client.room, client),
    "upload": handle_upload,
    "download": handle_download,
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
            raw_message = client.socket.recv(40960).decode('utf-8')
            if raw_message.startswith('{"type": "upload"'):
                while not raw_message.endswith('}'):
                    raw_message += client.socket.recv(40960).decode('utf-8')

            received_message = Message.from_json(raw_message)
            print(f"Received message from {client.name}:")
            print(raw_message)
            handle_message(client, received_message)
        except Exception:
            print(f"Error from client {client.name}, trying again...")


if __name__ == "__main__":
    serve_connections()
