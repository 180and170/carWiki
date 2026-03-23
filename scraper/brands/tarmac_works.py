"""Scraper for Tarmac Works - tarmacworks.com (Shopify-based)."""

import json
import re

from bs4 import BeautifulSoup

from ..config import BRANDS
from ..utils import absolute_url, fetch_page, get_session, polite_delay, download_image


def scrape():
    """Scrape Tarmac Works product catalog via Shopify JSON API."""
    brand = BRANDS["tarmac_works"]
    session = get_session()
    products = []

    print(f"[Tarmac Works] Starting scrape from {brand['website']}")

    products = _scrape_shopify_api(session)
    if not products:
        print("[Tarmac Works] API approach failed, trying HTML scrape")
        products = _scrape_html(session)

    print(f"[Tarmac Works] Completed with {len(products)} products")
    return products


def _scrape_shopify_api(session):
    """Scrape via Shopify products.json API."""
    products = []
    page = 1
    max_pages = 5

    while page <= max_pages:
        url = f"https://www.tarmacworks.com/collections/1-64-scale/products.json?page={page}&limit=50"
        resp = fetch_page(url, session)
        if not resp:
            break

        try:
            data = resp.json()
        except (json.JSONDecodeError, ValueError):
            break

        items = data.get("products", [])
        if not items:
            break

        for item in items:
            title = item.get("title", "")
            body_html = item.get("body_html", "")
            desc = BeautifulSoup(body_html, "lxml").get_text(strip=True) if body_html else ""

            images = item.get("images", [])
            image_url = images[0].get("src", "") if images else ""
            local_image = download_image(image_url, "tarmac_works", session) if image_url else ""

            variants = item.get("variants", [])
            price = variants[0].get("price", "") if variants else ""
            sku = variants[0].get("sku", "") if variants else ""

            handle = item.get("handle", "")
            product_url = f"https://www.tarmacworks.com/products/{handle}" if handle else ""

            products.append({
                "name": title,
                "sku": sku,
                "brand": "Tarmac Works",
                "scale": "1/64",
                "price": f"${price}" if price else "",
                "image": local_image or image_url,
                "image_url": image_url,
                "url": product_url,
                "description": desc[:500],
            })

        page += 1
        polite_delay()

    return products


def _scrape_html(session):
    """Fallback HTML scrape for Tarmac Works."""
    products = []
    url = "https://www.tarmacworks.com/collections/1-64-scale"
    resp = fetch_page(url, session)
    if not resp:
        return products

    soup = BeautifulSoup(resp.text, "lxml")

    for card in soup.select(".product-card, .grid-product, [class*='product']"):
        title_el = card.select_one(".product-card__title, .grid-product__title, a")
        title = title_el.get_text(strip=True) if title_el else ""
        if not title:
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

        price_el = card.select_one(".price, [class*='price']")
        price = price_el.get_text(strip=True) if price_el else ""

        products.append({
            "name": title,
            "sku": "",
            "brand": "Tarmac Works",
            "scale": "1/64",
            "price": price,
            "image": image_url,
            "image_url": image_url,
            "url": link,
            "description": "",
        })

    return products
