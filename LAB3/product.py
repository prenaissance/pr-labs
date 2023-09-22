from dataclasses import asdict, dataclass
import json
from typing import Dict

BASE_URL = "https://999.md"
URL = "https://999.md/ro/84193202"

@dataclass
class UserInfo:
    name: str
    join_year: int
    avatar_url: str
    profile_url: str

@dataclass
class DetailedProduct:
    name: str
    image_url: str
    description: str
    total_views: int
    user_info: UserInfo
    price_with_currency: str
    characteristics: Dict[str, str]
    region: str
    phone_number: str

def get_product(url: str):
    response = request()

def main():
    product_info = get_product(URL)
    with open("product_info.json", "w") as file:
        file.write(json.dumps(asdict(product_info), indent=2))

if __name__ == "__main__":
    main()