import os
import requests
from typing import Dict, Any, Optional, List

API_BASE_URL = os.getenv("BACKEND_API_URL", "http://backend:8000/api")

class GhostAPIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def get_stats(self) -> Optional[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/stats/overview", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            pass
        return None

    def get_graph(
        self,
        network_id: Optional[str] = None,
        min_risk: int = 0,
        max_nodes: int = 150
    ) -> Optional[Dict[str, Any]]:
        params = {"min_risk": min_risk, "max_nodes": max_nodes}
        if network_id:
            params["network_id"] = network_id
        try:
            resp = requests.get(f"{self.base_url}/graph", params=params, timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            pass
        return None

    def get_listings(
        self,
        page: int = 1,
        page_size: int = 20,
        country: Optional[str] = None,
        platform: Optional[str] = None,
        min_risk: int = 0,
        network_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        params = {"page": page, "page_size": page_size, "min_risk": min_risk}
        if country and country != "ALL":
            params["country"] = country
        if platform and platform != "ALL":
            params["platform"] = platform
        if network_id:
            params["network_id"] = network_id
        try:
            resp = requests.get(f"{self.base_url}/listings", params=params, timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            pass
        return None

    def get_listing_detail(self, listing_id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/listings/{listing_id}", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            pass
        return None

    def get_networks(self) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/networks", timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            pass
        return []

    def run_detection(self) -> Optional[Dict[str, Any]]:
        try:
            resp = requests.post(f"{self.base_url}/ingest/run-detection", timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            pass
        return None

client = GhostAPIClient()
