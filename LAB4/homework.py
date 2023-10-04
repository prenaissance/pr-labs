from dataclasses import asdict
import json
import socket
from typing import Dict
from product import Product
from http_server import Response
from bs4 import BeautifulSoup as bs

PORT = 4444

def request_http(path: str) -> Response:
    host = socket.gethostname()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    http_header = f"GET {path} HTTP/1.1\nHost: {host}\n\n"
    sock.connect((host, PORT))
    sock.send(bytes(http_header, "utf-8"))
    raw_data = sock.recv(2048)
    sock.close()
    head, *body_lines = str(raw_data, "utf-8").split("\n\n")
    body = "\n\n".join(body_lines)
    lines = head.split("\n")
    code = lines[0].split(" ")[1]
    headers = {}
    for line in lines[1:]:
        if line == "\r":
            break
        key, value = line.split(": ")
        headers[key] = value

    return Response(
        code,
        headers,
        body
    )

STATIC_PAGES = ["/", "/about", "/contacts"]

def get_product(path: str) -> Product:
    product_page = bs(request_http(path).body, "html.parser")
    name = product_page.find("h3").text
    paragraphs = product_page.find_all("p")
    author = paragraphs[0].text
    price = float(paragraphs[1].text)
    description = paragraphs[2].text
    return Product(name, author, price, description)

def get_products() -> Dict[str, dict]:
    products_page = bs(request_http("/products").body, "html.parser")
    product_anchors = products_page.find_all("a")
    product_links = [a["href"] for a in product_anchors]
    products = {}
    for link in product_links:
        products[link] = asdict(get_product(link))
    return products

def main():
    scraped_dict = {}
    pages = dict(
        (page, bs(request_http(page).body, "html.parser").prettify()) for page in STATIC_PAGES
    )
    scraped_dict["pages"] = pages
    scraped_dict["products"] = get_products()
    
    with open("scraped.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(scraped_dict, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()