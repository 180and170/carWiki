#!/usr/bin/env python3
"""Main scraper runner: orchestrates all brand scrapers and outputs JSON data."""

import json
import os
import sys
import traceback
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scraper.config import BRANDS, DATA_DIR, IMAGE_DIR
from scraper.brands import mini_gt, tarmac_works, inno64, tomica, hot_wheels, greenlight
from scraper.brands.generic import scrape_brand, GENERIC_BRANDS


SPECIALIZED_SCRAPERS = {
    "mini_gt": mini_gt.scrape,
    "tarmac_works": tarmac_works.scrape,
    "inno64": inno64.scrape,
    "tomica": tomica.scrape,
    "hot_wheels": hot_wheels.scrape,
    "green_light": greenlight.scrape,
}


def run_all():
    """Run all scrapers and save results."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)

    all_data = {
        "meta": {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_brands": len(BRANDS),
            "total_products": 0,
        },
        "brands": {},
        "products": {},
    }

    for brand_key, brand_info in BRANDS.items():
        all_data["brands"][brand_key] = {
            "key": brand_key,
            **brand_info,
        }

    total_products = 0

    for brand_key, scrape_fn in SPECIALIZED_SCRAPERS.items():
        print(f"\n{'='*60}")
        print(f"Scraping: {BRANDS[brand_key]['name']}")
        print(f"{'='*60}")
        try:
            products = scrape_fn()
            all_data["products"][brand_key] = products
            total_products += len(products)
            print(f"✓ {BRANDS[brand_key]['name']}: {len(products)} products")
        except Exception as e:
            print(f"✗ {BRANDS[brand_key]['name']}: Error - {e}")
            traceback.print_exc()
            all_data["products"][brand_key] = []

    for brand_key in GENERIC_BRANDS:
        print(f"\n{'='*60}")
        print(f"Scraping: {BRANDS[brand_key]['name']}")
        print(f"{'='*60}")
        try:
            products = scrape_brand(brand_key)
            all_data["products"][brand_key] = products
            total_products += len(products)
            print(f"✓ {BRANDS[brand_key]['name']}: {len(products)} products")
        except Exception as e:
            print(f"✗ {BRANDS[brand_key]['name']}: Error - {e}")
            traceback.print_exc()
            all_data["products"][brand_key] = []

    all_data["meta"]["total_products"] = total_products

    output_file = os.path.join(DATA_DIR, "catalog.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    brands_file = os.path.join(DATA_DIR, "brands.json")
    with open(brands_file, "w", encoding="utf-8") as f:
        json.dump(all_data["brands"], f, ensure_ascii=False, indent=2)

    for brand_key, products in all_data["products"].items():
        brand_file = os.path.join(DATA_DIR, f"products_{brand_key}.json")
        with open(brand_file, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"Total brands: {len(BRANDS)}")
    print(f"Total products scraped: {total_products}")
    print(f"Data saved to: {DATA_DIR}")
    print(f"Main catalog: {output_file}")

    return all_data


if __name__ == "__main__":
    run_all()
