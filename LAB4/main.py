from product import Product
import json
import regex

from http_server import HttpServer, Request, Response, NOT_FOUND_RESPONSE



# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 4444

with open("pages/products.template.html", "r", encoding="utf-8") as file:
    PRODUCTS_TEMPLATE = file.read()

with open("./products.json", "r", encoding="utf-8") as file:
    dicts = json.load(file)
    PRODUCTS = [Product(**d) for d in dicts]

def products_handler(request: Request) -> Response:
    products_view = "\n".join([f"""
                                <article style="border: 1px solid brown">
                                    <h3>{product.name}</h3>
                                    <p>{product.author}</p>
                                    <p>{product.price}</p>
                                    <p>{product.description}</p>
                                    <a href="/product/{index}">View</a>
                                </article>""" for (index, product) in enumerate(PRODUCTS)])
    html_content = PRODUCTS_TEMPLATE.replace("{{products}}", products_view)

    return Response(200, {"Content-Type": "text/html"}, html_content)

PRODUCT_REGEX = r"^/product/\d+$"
def product_handler(request: Request) -> Response:
    index = int(request.path.split("/")[-1])
    if index < 0 or index >= len(PRODUCTS):
        return NOT_FOUND_RESPONSE
    product = PRODUCTS[index]
    html_content = f"""
                    <article style="border: 1px solid brown">
                        <h3>{product.name}</h3>
                        <p>{product.author}</p>
                        <p>{product.price}</p>
                        <p>{product.description}</p>
                    </article>
                    <br/>
                    <a href="/products">Back</a>"""

    return Response(200, {"Content-Type": "text/html"}, html_content)

def main():
    http_server = HttpServer()
    http_server.add_html_file_handler("/", "pages/index.html")
    http_server.add_html_file_handler("/about", "pages/about.html")
    http_server.add_html_file_handler("/contacts", "pages/contacts.html")
    http_server.add_handler(lambda p: p == "/products", products_handler)
    http_server.add_handler(lambda p: regex.match(PRODUCT_REGEX, p), product_handler)
    
    http_server.serve(SERVER_HOST, SERVER_PORT)

if __name__ == "__main__":
    main()