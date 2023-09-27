from dataclasses import asdict, dataclass
import json
from urllib.parse import urljoin
import requests
from typing import Dict, List, Literal, Tuple, Union
from bs4 import BeautifulSoup as bs

BASE_URL = "https://999.md"
URL = "https://999.md/ro/84322839"

@dataclass
class UserInfo:
    name: str
    join_year: int
    profile_url: str
    avatar_url: str

@dataclass
class DetailedProduct:
    name: str
    image_urls: List[str]
    description: str
    total_views: int
    today_views: int
    price_with_currency: str
    region: str
    phone_number: str
    features: Dict[str, Dict[str, Union[str, Literal[True]]]]
    user_info: UserInfo
    url: str = URL

def get_views(raw_text: str) -> Tuple[int, int]:
    total_views_raw_text, today_views_raw_text = raw_text.split(":")[1].split("(")
    total_views = int(total_views_raw_text.replace(" ", ""))
    today_views = int(today_views_raw_text.split(" ")[1][:-1])
    return total_views, today_views

def get_features(page: bs) -> Dict[str, Dict[str, str]]:
    feature_containers = page.select(".adPage__content__features__col")
    features: Dict[str, Dict[str, str]] = {}
    for container in feature_containers:
        feature_name_elements = container.select("h2")
        for feature_name_element in feature_name_elements:
            feature_name = feature_name_element.text.strip()
            feature_list_container = feature_name_element.find_next_sibling("ul")
            if not feature_list_container:
                continue
            feature_items = feature_list_container.select("li")
            features[feature_name] = dict(
                tuple(map(lambda x: x.text.strip(), item.select("span")))
                    if len(item.select("span")) == 2
                    else (item.text.strip(), True)
                for item in feature_items
            )

    return features

def get_user_info(page: bs) -> UserInfo:
    container = page.select_one(".adPage__aside__stats__owner > dd")
    anchor = container.select_one("a")
    name = anchor.text.strip()
    join_year = int(container.select_one("span").text.split(" ")[-1].strip())
    profile_url = urljoin(BASE_URL, anchor.get("href"))
    
    profile_page = bs(requests.get(profile_url).text, "html.parser")
    avatar_url = profile_page.select_one(".avatar-wrapper > img").get("src")

    return UserInfo(
        name = name,
        join_year = join_year,
        profile_url = profile_url,
        avatar_url = avatar_url
    )

def get_product(url: str):
    response = requests.get(url)
    page = bs(response.text, "html.parser")
    name = page.select_one("header > h1").text.strip()
    image_urls = [anchor.get("data-src") for anchor in page.select("a.js-fancybox.mfp-zoom.mfp-image")]
    description = page.select_one(".adPage__content__description").text.strip()
    total_views_raw_text = page.select_one(".adPage__aside__stats__views").text
    total_views, today_views = get_views(total_views_raw_text)
    price_with_currency = page\
        .select_one(".tooltip.adPage__content__price-feature__prices__price.is-main")\
        .text.replace(" ", "")
    region = page.select_one(".adPage__content__region").text.strip()
    phone_number_element = page.select_one(".js-phone-number.adPage__content__phone a")
    phone_number = phone_number_element.get("href").replace("tel:", "") if phone_number_element else None

    features = get_features(page)
    user_info = get_user_info(page)

    return DetailedProduct(
        name = name,
        image_urls = image_urls,
        description = description,
        total_views = total_views,
        today_views = today_views,
        price_with_currency = price_with_currency,
        region = region,
        phone_number = phone_number,
        features = features,
        user_info = user_info
    )

def homework():
    product_info = get_product(URL)
    product_info.user_info = asdict(product_info.user_info)
    with open("product_info.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(asdict(product_info), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    homework()