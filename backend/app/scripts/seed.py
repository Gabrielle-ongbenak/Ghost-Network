import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.database import engine, SessionLocal, Base
from app.models import Listing, Contact, ListingContact, ListingLink, NetworkCluster, RiskSignal
from app.services.seed_loader import load_seed_data

def run_seed():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")

    db = SessionLocal()
    try:
        count = db.query(Listing).count()
        if count == 0:
            print("Database is empty. Loading seed listings...")
            loaded = load_seed_data(db)
            print(f"Seed loading complete. {loaded} listings imported.")
        else:
            print(f"Database already contains {count} listings. Ensuring detection & clustering are up to date...")
            from app.services.detector import detect_listing_links
            from app.services.scorer import score_all_listings
            from app.services.graph_service import cluster_and_save_networks

            detect_listing_links(db)
            score_all_listings(db)
            cluster_and_save_networks(db)
            print("Detection & network clustering refreshed.")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
