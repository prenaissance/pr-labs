from dataclasses import dataclass


@dataclass
class Product:
    name: str
    author: str
    price: int
    description: str