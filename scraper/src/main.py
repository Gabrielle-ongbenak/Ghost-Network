import os
import json
import requests
from typing import List, Dict, Any

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000/api")

def push_listings_to_backend(listings: List[Dict[str, Any]]) -> bool:
    """Sends structured scraped listings to the FastAPI backend."""
    try:
        resp = requests.post(f"{BACKEND_API_URL}/ingest/bulk", json={"listings": listings}, timeout=10)
        if resp.status_code == 201:
            print(f"Successfully pushed {len(listings)} listings to backend.")
            return True
        else:
            print(f"Failed to push listings: {resp.status_code} - {resp.text}")
    except requests.RequestException as e:
        print(f"Error connecting to backend: {e}")
    return False

def main():
    print("Ghost Networks Scraper Runner Initialized.")
    print("Scraping target countries: Cameroon (CMR), Nigeria (NGA), Kenya (KEN)")
    # For standalone runs or Apify actor testing:
    sample_path = os.path.join(os.path.dirname(__file__), "../../data/seed/listings_sample.json")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            sample_data = json.load(f)
            print(f"Loaded {len(sample_data)} sample listings from seed archive.")

if __name__ == "__main__":
    main()
