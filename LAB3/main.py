
from dataclasses import asdict, dataclass
import json
from typing import List, Union
from bs4 import BeautifulSoup as bs
import requests
from urllib.parse import urljoin

BASE_URL = "https://999.md"
cookie_jar={
    "show_all_checked_childrens":	"no",
    "selected_currency":            "usd",
    "hide_duplicates":          	"yes",
    "simpalsid.lang":              	"ro",
    "view_type":                	"detail",
}

@dataclass
class Product:
    link: str
    name: str
    price: float

def get_next_page_url(page: bs) -> Union[str, None]:
    url_items = page.select("nav.paginator.cf li > a")
    current_page = page.select_one("nav.paginator.cf li.current > a")
    if list(url_items).index(current_page) == len(url_items) - 1:
        return None

    return urljoin(BASE_URL, current_page.get("href"))

def get_page_items(url: str, max_depth: int = 10) -> List[Product]:
    response = requests.get(url, cookies=cookie_jar)
    page = bs(response.text, "html.parser")
    cards = page.select("ul.ads-list-detail > li")
    
    products: List[Product] = []
    for card in cards:
        link = urljoin(BASE_URL, card.select_one("div.ads-list-detail-item-title > a").get("href"))
        name = card.select_one("div.ads-list-detail-item-title").text.strip()
        price_string = card.select_one("div.ads-list-detail-item-price").text\
            .replace("≈", "")\
            .replace("$", "")\
            .strip()\
            .split()[0]
        price = None if price_string == "negociabil" else float(price_string)
        products.append(Product(link, name, price))
    
    if max_depth > 1:
        next_page_url = get_next_page_url(page)
        if next_page_url:
            products.extend(get_page_items(next_page_url, max_depth - 1))
    
    return products

def in_class():
    items = get_page_items("https://999.md/ro/list/computers-and-office-equipment/video?view_type=detail", 5)
    # write as json
    with open("items.json", "w", encoding="utf-8") as file:
        file.write(json.dumps([asdict(item) for item in items], indent=2, ensure_ascii=False))

if __name__ == '__main__':
    in_class()