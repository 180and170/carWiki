"""Generic scraper for brands where we mainly want brand info + any available products."""

from bs4 import BeautifulSoup

from ..config import BRANDS
from ..utils import absolute_url, fetch_page, get_session, safe_text, download_image


GENERIC_BRANDS = [
    "era_car", "matchbox", "johnny_lightning",
    "majorette", "siku", "kaido_house", "pop_race",
]


def scrape_brand(brand_key):
    """Scrape a brand using generic approach."""
    brand = BRANDS[brand_key]
    session = get_session()
    products = []

    print(f"[{brand['name']}] Starting scrape from {brand['website']}")

    resp = fetch_page(brand["website"], session)
    if not resp:
        print(f"[{brand['name']}] Failed to fetch main page")
        return products

    soup = BeautifulSoup(resp.text, "lxml")

    product_selectors = [
        ".product-card", ".product-item", ".product",
        "[class*='product']", ".grid-item", ".item",
        ".collection-item", ".card",
    ]

    for selector in product_selectors:
        items = soup.select(selector)
        if len(items) > 2:
            for item in items[:30]:
                product = _parse_generic_item(item, brand["website"], brand["name"], brand_key, session)
                if product:
                    products.append(product)
            break

    if not products and brand.get("catalog_url"):
        resp2 = fetch_page(brand["catalog_url"], session)
        if resp2:
            soup2 = BeautifulSoup(resp2.text, "lxml")
            for selector in product_selectors:
                items = soup2.select(selector)
                if len(items) > 2:
                    for item in items[:30]:
                        product = _parse_generic_item(
                            item, brand["catalog_url"], brand["name"], brand_key, session
                        )
                        if product:
                            products.append(product)
                    break

    print(f"[{brand['name']}] Completed with {len(products)} products")
    return products


def _parse_generic_item(item, base_url, brand_name, brand_key, session):
    """Parse a product from generic HTML structure."""
    title_el = item.select_one("h2, h3, h4, .title, .name, a")
    title = safe_text(title_el)
    if not title or len(title) < 3:
        return None

    link_el = item.select_one("a[href]")
    link = absolute_url(base_url, link_el.get("href", "")) if link_el else ""

    img_el = item.select_one("img")
    image_url = ""
    if img_el:
        image_url = img_el.get("src") or img_el.get("data-src") or img_el.get("data-lazy-src", "")
        image_url = absolute_url(base_url, image_url)
        if image_url.startswith("//"):
            image_url = "https:" + image_url

    price_el = item.select_one("[class*='price'], .price")
    price = safe_text(price_el)

    return {
        "name": title,
        "sku": "",
        "brand": brand_name,
        "scale": "1/64",
        "price": price,
        "image": image_url,
        "image_url": image_url,
        "url": link,
        "description": "",
    }


def scrape_all_generic():
    """Scrape all generic brands."""
    results = {}
    for brand_key in GENERIC_BRANDS:
        results[brand_key] = scrape_brand(brand_key)
    return results
