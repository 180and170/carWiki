"""Scraper for Mini GT (TSM Model) - minigt.com"""

import re

from bs4 import BeautifulSoup

from ..config import BRANDS
from ..utils import absolute_url, fetch_page, get_session, polite_delay, safe_text, download_image


def scrape():
    """Scrape Mini GT product catalog."""
    brand = BRANDS["mini_gt"]
    session = get_session()
    products = []

    print(f"[Mini GT] Starting scrape from {brand['catalog_url']}")

    base_url = "https://minigt.com/index.php?action=product-list"
    resp = fetch_page(base_url, session)
    if not resp:
        print("[Mini GT] Failed to fetch catalog page, trying alternative approach")
        return _scrape_from_api(session)

    soup = BeautifulSoup(resp.text, "lxml")

    product_links = []
    for a in soup.select("a[href*='product-detail']"):
        href = absolute_url(base_url, a.get("href", ""))
        if href and href not in product_links:
            product_links.append(href)

    if not product_links:
        for a in soup.select(".product-item a, .product-card a, .item a"):
            href = absolute_url(base_url, a.get("href", ""))
            if href and href not in product_links:
                product_links.append(href)

    print(f"[Mini GT] Found {len(product_links)} product links")

    for i, link in enumerate(product_links[:50]):
        polite_delay()
        product = _scrape_product_page(link, session)
        if product:
            products.append(product)
        if (i + 1) % 10 == 0:
            print(f"[Mini GT] Scraped {i + 1}/{min(len(product_links), 50)} products")

    print(f"[Mini GT] Completed with {len(products)} products")
    return products


def _scrape_from_api(session):
    """Try to scrape from API endpoints or alternative pages."""
    products = []
    page = 1
    max_pages = 5

    while page <= max_pages:
        url = f"https://minigt.com/index.php?action=product-list&page={page}"
        resp = fetch_page(url, session)
        if not resp:
            break

        soup = BeautifulSoup(resp.text, "lxml")
        items = soup.select(".product-item, .product-card, .item-box, [class*='product']")
        if not items:
            break

        for item in items:
            product = _parse_list_item(item, url)
            if product:
                products.append(product)

        page += 1
        polite_delay()

    return products


def _scrape_product_page(url, session):
    """Scrape a single product detail page."""
    resp = fetch_page(url, session)
    if not resp:
        return None

    soup = BeautifulSoup(resp.text, "lxml")

    title = safe_text(soup.select_one("h1, .product-title, .product-name"))
    if not title:
        title = safe_text(soup.select_one("title"))

    img_el = soup.select_one(".product-image img, .product-detail img, .main-image img")
    image_url = ""
    if img_el:
        image_url = img_el.get("src") or img_el.get("data-src", "")
        image_url = absolute_url(url, image_url)

    local_image = download_image(image_url, "mini_gt", session) if image_url else ""

    sku_match = re.search(r"(MGT\d+)", title) or re.search(r"(MGT\d+)", resp.text[:5000])
    sku = sku_match.group(1) if sku_match else ""

    desc_el = soup.select_one(".product-description, .product-info, .description")
    description = safe_text(desc_el)

    price_el = soup.select_one(".price, .product-price, [class*='price']")
    price = safe_text(price_el)

    return {
        "name": title,
        "sku": sku,
        "brand": "Mini GT",
        "scale": "1/64",
        "price": price,
        "image": local_image or image_url,
        "image_url": image_url,
        "url": url,
        "description": description,
    }


def _parse_list_item(item, base_url):
    """Parse a product from a list/grid view."""
    title_el = item.select_one("a, .title, .name, h3, h4")
    title = safe_text(title_el)
    if not title:
        return None

    link_el = item.select_one("a[href]")
    url = absolute_url(base_url, link_el.get("href", "")) if link_el else ""

    img_el = item.select_one("img")
    image_url = ""
    if img_el:
        image_url = img_el.get("src") or img_el.get("data-src", "")
        image_url = absolute_url(base_url, image_url)

    price_el = item.select_one(".price, [class*='price']")
    price = safe_text(price_el)

    return {
        "name": title,
        "sku": "",
        "brand": "Mini GT",
        "scale": "1/64",
        "price": price,
        "image": image_url,
        "image_url": image_url,
        "url": url,
        "description": "",
    }
