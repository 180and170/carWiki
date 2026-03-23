"""Utility functions for scraping."""

import hashlib
import os
import random
import time
from urllib.parse import urljoin, urlparse

import requests

from .config import HEADERS, IMAGE_DIR, REQUEST_DELAY, REQUEST_TIMEOUT


def get_session():
    """Create a requests session with default headers."""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def polite_delay():
    """Sleep for a random interval to be polite to servers."""
    delay = random.uniform(*REQUEST_DELAY)
    time.sleep(delay)


def fetch_page(url, session=None, timeout=REQUEST_TIMEOUT):
    """Fetch a page and return the response, with error handling."""
    if session is None:
        session = get_session()
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        print(f"  [ERROR] Failed to fetch {url}: {e}")
        return None


def download_image(url, brand_key, session=None):
    """Download an image and save it locally. Returns local relative path."""
    if not url or url.startswith("data:"):
        return ""

    if session is None:
        session = get_session()

    brand_img_dir = os.path.join(IMAGE_DIR, brand_key)
    os.makedirs(brand_img_dir, exist_ok=True)

    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    ext = os.path.splitext(urlparse(url).path)[1] or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        ext = ".jpg"
    filename = f"{url_hash}{ext}"
    filepath = os.path.join(brand_img_dir, filename)

    if os.path.exists(filepath):
        return f"data/images/{brand_key}/{filename}"

    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT, stream=True)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        return f"data/images/{brand_key}/{filename}"
    except requests.RequestException as e:
        print(f"  [WARN] Failed to download image {url}: {e}")
        return ""


def safe_text(element):
    """Safely extract text from a BeautifulSoup element."""
    if element is None:
        return ""
    return element.get_text(strip=True)


def absolute_url(base, relative):
    """Convert a relative URL to absolute."""
    if not relative:
        return ""
    if relative.startswith(("http://", "https://")):
        return relative
    return urljoin(base, relative)
