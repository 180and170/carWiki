"""Scraper for Tomica (Takara Tomy) via US Tomy store."""

from bs4 import BeautifulSoup

from ..config import BRANDS
from ..utils import absolute_url, fetch_page, get_session, polite_delay, safe_text, download_image


def scrape():
    """Scrape Tomica product catalog from US Tomy store."""
    brand = BRANDS["tomica"]
    session = get_session()
    products = []

    print(f"[Tomica] Starting scrape from US Tomy store")

    url = "https://us.tomy.com/our-brands/tomica-limited-vintage/shop-all/"
    resp = fetch_page(url, session)
    if resp:
        soup = BeautifulSoup(resp.text, "lxml")
        for card in soup.select(".product-card, .product, [class*='product-item'], .card"):
            title_el = card.select_one("h2, h3, h4, .card-title, .productView-title")
            title = safe_text(title_el)

            link_el = card.select_one("a[href*='/products/'], a[href*='tomica']")
            if not link_el:
                link_el = card.select_one("a[href]")
            link = absolute_url(url, link_el.get("href", "")) if link_el else ""

            img_el = card.select_one("img")
            image_url = ""
            if img_el:
                image_url = img_el.get("src") or img_el.get("data-src", "")
                image_url = absolute_url(url, image_url)

            local_image = download_image(image_url, "tomica", session) if image_url else ""

            price_el = card.select_one(".price, [class*='price']")
            price = safe_text(price_el)
            price = price.replace("MSRP:", "").strip() if price else ""

            if link and image_url:
                products.append({
                    "name": title if title else f"Tomica Limited Vintage",
                    "sku": "",
                    "brand": "Tomica",
                    "scale": "1/64",
                    "price": price,
                    "image": local_image or image_url,
                    "image_url": image_url,
                    "url": link,
                    "description": "",
                })

    if not products:
        products = _scrape_japan_site(session)

    print(f"[Tomica] Completed with {len(products)} products")
    return products


def _scrape_japan_site(session):
    """Fallback: scrape Japan Takara Tomy site."""
    products = []
    url = "https://www.takaratomy.co.jp/products/tomica/"
    resp = fetch_page(url, session)
    if not resp:
        return products

    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    for item in soup.select("a[href]"):
        img = item.select_one("img[src*='tomica'], img[src*='product']")
        if not img:
            continue
        src = img.get("src", "")
        if "logo" in src or "icon" in src or "nav" in src or "banner" in src:
            continue

        title = img.get("alt", "") or safe_text(item)
        if not title or len(title) < 2:
            continue

        image_url = absolute_url(url, src)
        link = absolute_url(url, item.get("href", ""))

        products.append({
            "name": title,
            "sku": "",
            "brand": "Tomica",
            "scale": "1/64",
            "price": "",
            "image": image_url,
            "image_url": image_url,
            "url": link,
            "description": "",
        })

    return products
