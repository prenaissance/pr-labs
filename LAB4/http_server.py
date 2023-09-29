from dataclasses import dataclass
import socket
from typing import Callable, List


@dataclass
class Request:
    method: str
    path: str
    headers: dict
    body: str

@dataclass
class Response:
    status_code: int
    headers: dict
    body: str

@dataclass
class RouteHandler:
    path_matcher: Callable[[str], bool]
    handler: Callable[[Request], Response]

NOT_FOUND_RESPONSE = Response(404, {"Content-Type": "text/html"}, "<h1>Not found</h1>")


class HttpServer:
    _handlers: List[RouteHandler] = []
    _socket_server: socket.socket = None

    def _parse_request(self, request: str) -> Request:
        lines = request.split("\n")
        method, path, _ = lines[0].split(" ")
        headers = {}
        body = ""
        for line in lines[1:]:
            if line == "\r":
                break
            key, value = line.split(": ")
            headers[key] = value
        return Request(method, path, headers, body)

    def _create_response(self, response: Response) -> str:
        formatted_headers = "\n".join(
            [f"{key}: {value}" for key, value in response.headers.items()])
        return f"HTTP/1.1 {response.status_code}\n{formatted_headers}\n\n{response.body}"

    def add_handler(self, path_matcher: Callable[[str], bool], handler: Callable[[Request], Response]):
        self._handlers.append(RouteHandler(path_matcher, handler))

    def add_html_file_handler(self, path: str, file_path: str):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        self.add_handler(lambda p: p == path, lambda _: Response(200, {"Content-Type": "text/html"}, content))

    def serve(self, host: str, port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen(1)
            print('Listening on port %s ...' % port)

            while True:
                # Wait for client connections
                client_connection, client_address = server_socket.accept()

                # Get the client request
                request = self._parse_request(
                    client_connection.recv(1024).decode())

                handler = next(
                    (handler for handler in self._handlers if handler.path_matcher(request.path)), None)
                final_handler = NOT_FOUND_RESPONSE if handler is None else handler.handler(request)
                response = self._create_response(final_handler)
                client_connection.sendall(response.encode())
                client_connection.close()
