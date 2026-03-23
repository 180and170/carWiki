"""Scraper for INNO64 - inno64model.com"""

from bs4 import BeautifulSoup

from ..config import BRANDS
from ..utils import absolute_url, fetch_page, get_session, polite_delay, safe_text, download_image


def scrape():
    """Scrape INNO64 product catalog."""
    brand = BRANDS["inno64"]
    session = get_session()
    products = []

    print(f"[INNO64] Starting scrape from {brand['catalog_url']}")

    page = 1
    max_pages = 5

    while page <= max_pages:
        url = f"https://www.inno64model.com/shop/page/{page}/"
        resp = fetch_page(url, session)
        if not resp:
            break

        soup = BeautifulSoup(resp.text, "lxml")
        items = soup.select(".product, .product-item, li.product, .products .item")
        if not items:
            items = soup.select("[class*='product']")

        if not items:
            break

        for item in items:
            product = _parse_product(item, url, session)
            if product:
                products.append(product)

        next_link = soup.select_one("a.next, .pagination a.next, a[rel='next']")
        if not next_link:
            break

        page += 1
        polite_delay()

    print(f"[INNO64] Completed with {len(products)} products")
    return products


def _parse_product(item, base_url, session):
    """Parse a product element."""
    title_el = item.select_one(".woocommerce-loop-product__title, .product-title, h2, h3, a")
    title = safe_text(title_el)
    if not title:
        return None

    link_el = item.select_one("a[href*='product'], a[href*='shop']")
    if not link_el:
        link_el = item.select_one("a[href]")
    url = absolute_url(base_url, link_el.get("href", "")) if link_el else ""

    img_el = item.select_one("img")
    image_url = ""
    if img_el:
        image_url = img_el.get("src") or img_el.get("data-src", "")
        image_url = absolute_url(base_url, image_url)

    local_image = download_image(image_url, "inno64", session) if image_url else ""

    price_el = item.select_one(".price, .woocommerce-Price-amount, [class*='price']")
    price = safe_text(price_el)

    return {
        "name": title,
        "sku": "",
        "brand": "INNO64",
        "scale": "1/64",
        "price": price,
        "image": local_image or image_url,
        "image_url": image_url,
        "url": url,
        "description": "",
    }
