"""Scraper for Hot Wheels (Mattel)."""

from bs4 import BeautifulSoup

from ..config import BRANDS
from ..utils import absolute_url, fetch_page, get_session, safe_text, download_image


def scrape():
    """Scrape Hot Wheels product information.

    Hot Wheels site is heavily JS-rendered, so we focus on
    extracting available static content and brand information.
    """
    brand = BRANDS["hot_wheels"]
    session = get_session()
    products = []

    print(f"[Hot Wheels] Starting scrape from {brand['website']}")

    url = "https://shop.mattel.com/collections/hot-wheels-cars"
    resp = fetch_page(url, session)
    if resp:
        soup = BeautifulSoup(resp.text, "lxml")
        for card in soup.select(".product-card, [class*='product'], .grid-item"):
            title_el = card.select_one("h3, h4, .product-title, a")
            title = safe_text(title_el)
            if not title or len(title) < 3:
                continue

            link_el = card.select_one("a[href*='/products/']")
            link = absolute_url(url, link_el.get("href", "")) if link_el else ""

            img_el = card.select_one("img")
            image_url = ""
            if img_el:
                image_url = img_el.get("src") or img_el.get("data-src", "")
                image_url = absolute_url(url, image_url)
                if image_url.startswith("//"):
                    image_url = "https:" + image_url

            price_el = card.select_one("[class*='price']")
            price = safe_text(price_el)

            products.append({
                "name": title,
                "sku": "",
                "brand": "Hot Wheels",
                "scale": "1/64",
                "price": price,
                "image": image_url,
                "image_url": image_url,
                "url": link,
                "description": "",
            })

    print(f"[Hot Wheels] Completed with {len(products)} products")
    return products
