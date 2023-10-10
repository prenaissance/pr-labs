import json
from os import makedirs, path
import socket
import threading
from typing import Callable, Dict
import base64

from common import Message
# Server configuration
HOST = '127.0.0.1'  # Server's IP address
PORT = 12345  # Server's port
MEDIA_PATH = ".\client_media"
name: str
room_name: str
# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Connect to the server
client_socket.connect((HOST, PORT))


def close_client():
    client_socket.close()
    print("Disconnected from server")


def upload(file_path):
    file_name = path.basename(file_path)
    if not path.exists(file_path):
        print(f"File {file_path} does not exist")
        return
    with open(file_path, "rb") as file:
        data = file.read()
    base64_data = base64.b64encode(data).decode("utf-8")
    message = Message("upload", {"file_name": file_name, "data": base64_data})
    client_socket.send(message.to_json().encode("utf-8"))


def download(file_name):
    message = Message("download", {"file_name": file_name})
    client_socket.send(message.to_json().encode("utf-8"))


def handle_download(payload: dict):
    file_path = path.join(MEDIA_PATH, f"{room_name}_{name}", payload["file_name"])
    data = base64.b64decode(payload["data"])
    if not path.exists(path.dirname(file_path)):
        makedirs(path.dirname(file_path))
    with open(file_path, "wb") as file:
        file.write(data)
    print(f"File {payload['file_name']} downloaded successfully")


def echo_handler(payload): return print(payload["message"])


message_handlers: Dict[str, Callable[[dict], None]] = {
    "acknowledge": echo_handler,
    "notification": echo_handler,
    "message": lambda payload: print(f"{payload['sender']}: {payload['text']}"),
    "download": handle_download,
}


def listen_for_messages():
    while True:
        try:
            raw_message = client_socket.recv(100_000).decode('utf-8')
            if not raw_message:
                return
            message = Message.from_json(raw_message)
            message_handlers[message.type](message.payload)
        except Exception as e:
            print(f"Error: {e}")


# Start a thread for listening for messages
listen_thread = threading.Thread(target=listen_for_messages)
listen_thread.daemon = True


def main():
    global name, room_name
    name = input("Name: ")
    room_name = input("Room name: ")
    connect_message = Message("connect", {"name": name, "room": room_name})
    client_socket.send(connect_message.to_json().encode("utf-8"))
    listen_thread.start()
    get_input()


def get_input():
    message = input()
    if message.lower() == 'exit':
        close_client()
        return
    if message.lower().startswith("upload"):
        upload(message.split(" ")[1])
        get_input()
        return
    if message.lower().startswith("download"):
        download(message.split(" ")[1])
        get_input()
        return

    send_message = Message("message", {"text": message})
    client_socket.send(send_message.to_json().encode('utf-8'))
    get_input()


if __name__ == "__main__":
    main()
