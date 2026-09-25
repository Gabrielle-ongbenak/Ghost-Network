"""
Data loader and scraper simulation module for African job boards.
Loads seed and verified pan-African listings (Cameroon, Nigeria, Kenya),
or parses custom input listings supplied by the user.
"""

import os
import json
from typing import List, Dict, Any


def load_bundled_seed_listings() -> List[Dict[str, Any]]:
    """Loads bundled reference dataset containing cross-border scam syndicates."""
    data_path = os.path.join(os.path.dirname(__file__), "../data/seed_listings.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_target_listings(
    target_countries: List[str],
    search_keywords: List[str],
    max_listings: int = 30,
    custom_listings: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves job postings to be analyzed:
    - If custom_listings are provided, uses them.
    - Otherwise, fetches from bundled African dataset filtered by country and keywords.
    """
    if custom_listings and len(custom_listings) > 0:
        return custom_listings[:max_listings]

    seed_items = load_bundled_seed_listings()
    filtered = []

    upper_countries = [c.upper() for c in target_countries] if target_countries else ["CMR", "NGA", "KEN"]
    lower_keywords = [k.lower() for k in search_keywords] if search_keywords else []

    for item in seed_items:
        # Check country match
        c_code = (item.get("country_code") or item.get("country") or "").upper()
        if upper_countries and c_code not in upper_countries:
            continue

        # Check keyword match
        if lower_keywords:
            text = f"{item.get('title', '')} {item.get('description', '')}".lower()
            if not any(k in text for k in lower_keywords):
                # If no exact keyword match, keep if it has any scam fee mention
                if not any(fee in text for fee in ("fee", "frais", "kit", "dossier", "registration")):
                    continue

        filtered.append(item)
        if len(filtered) >= max_listings:
            break

    # If filter was too restrictive, return all matching the countries up to max_listings
    if not filtered:
        for item in seed_items:
            c_code = (item.get("country_code") or item.get("country") or "").upper()
            if c_code in upper_countries:
                filtered.append(item)
                if len(filtered) >= max_listings:
                    break

    return filtered[:max_listings]
