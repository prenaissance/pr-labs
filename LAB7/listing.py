
from dataclasses import asdict, dataclass
import json
from typing import Generator, List, Union
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

def get_page_links_generator(url: str, max_depth: int = 10) :
    response = requests.get(url, cookies=cookie_jar)
    page = bs(response.text, "html.parser")
    cards = page.select("ul.ads-list-detail > li")

    for card in cards:
        link = urljoin(BASE_URL, card.select_one("div.ads-list-detail-item-title > a").get("href"))
        try:
            link.index("booster")
        except ValueError:
            yield link

    if max_depth > 1:
        next_page_url = get_next_page_url(page)
        if next_page_url:
            for link in get_page_links_generator(next_page_url, max_depth - 1):
                yield link
