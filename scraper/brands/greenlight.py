"""Scraper for GreenLight Collectibles - greenlighttoys.com (WooCommerce)."""

from bs4 import BeautifulSoup

from ..config import BRANDS
from ..utils import absolute_url, fetch_page, get_session, polite_delay, safe_text, download_image


def scrape():
    """Scrape GreenLight 1/64 series catalog."""
    brand = BRANDS["green_light"]
    session = get_session()
    products = []

    print(f"[GreenLight] Starting scrape from greenlighttoys.com")

    url = "https://www.greenlighttoys.com/product-category/1-64/"
    resp = fetch_page(url, session)
    if not resp:
        return products

    soup = BeautifulSoup(resp.text, "lxml")
    series_links = []

    for item in soup.select("li.product a[href*='/product/']"):
        href = item.get("href", "")
        if href and href not in series_links:
            series_links.append(href)

    if not series_links:
        for item in soup.select("a[href*='/product/']"):
            href = item.get("href", "")
            if href and href not in series_links:
                series_links.append(href)

    print(f"[GreenLight] Found {len(series_links)} series")

    for i, series_url in enumerate(series_links):
        title_parts = series_url.rstrip("/").split("/")
        series_name = title_parts[-1].replace("-", " ").title() if title_parts else ""

        img_el = soup.select_one(f"a[href='{series_url}'] img")
        image_url = ""
        if img_el:
            image_url = img_el.get("src") or img_el.get("data-src", "")

        local_image = download_image(image_url, "green_light", session) if image_url else ""

        products.append({
            "name": f"GreenLight {series_name}",
            "sku": "",
            "brand": "GreenLight",
            "scale": "1/64",
            "price": "",
            "image": local_image or image_url,
            "image_url": image_url,
            "url": series_url,
            "description": f"GreenLight 1:64 {series_name} series",
        })

    print(f"[GreenLight] Completed with {len(products)} series/products")
    return products
