import re
from typing import List, Tuple
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from app.models.listing import Listing
from app.models.link import ListingLink

def sanitize_text_for_similarity(text: str) -> str:
    """Removes emails, phones, URLs and excess whitespace for fair template comparison."""
    if not text:
        return ""
    # Strip emails
    t = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", "", text)
    # Strip phones / numbers
    t = re.sub(r"\+?\d[\d -]{7,}\d", "", t)
    # Strip URLs
    t = re.sub(r"https?://\S+", "", t)
    # Lowercase & normalize spaces
    t = re.sub(r"\s+", " ", t.lower()).strip()
    return t

def detect_listing_links(db: Session) -> int:
    """
    Scans listings in the database to discover:
    1. Shared contact edges (reused phone, reused email)
    2. Recycled text similarity edges using RapidFuzz (>= 85%)
    Saves edges into the listing_links table. Returns the number of created links.
    """
    listings = db.query(Listing).all()
    if not listings or len(listings) < 2:
        return 0

    # Clear previous links to ensure fresh recalculation
    db.query(ListingLink).delete()
    db.flush()

    links_to_create = []
    seen_pairs = set()

    # 1. Contact reuse links
    # Map normalized_contact_value -> list of listing_ids
    contact_map = {}
    for listing in listings:
        for contact in listing.contacts:
            contact_map.setdefault((contact.contact_type, contact.normalized_value), []).append(listing.id)

    for (c_type, c_val), listing_ids in contact_map.items():
        if len(listing_ids) > 1:
            for i in range(len(listing_ids)):
                for j in range(i + 1, len(listing_ids)):
                    pair = tuple(sorted([str(listing_ids[i]), str(listing_ids[j])]))
                    link_type = "REUSED_PHONE" if c_type == "PHONE" else "REUSED_EMAIL"
                    if (pair, link_type) not in seen_pairs:
                        seen_pairs.add((pair, link_type))
                        links_to_create.append(
                            ListingLink(
                                source_listing_id=listing_ids[i],
                                target_listing_id=listing_ids[j],
                                link_type=link_type,
                                weight=1.0,
                                metadata_info={"matched_value": c_val, "contact_type": c_type}
                            )
                        )

    # 2. Text similarity links using Rapidfuzz
    preprocessed_texts = {l.id: sanitize_text_for_similarity(l.description) for l in listings}

    for i in range(len(listings)):
        id_a = listings[i].id
        text_a = preprocessed_texts[id_a]
        len_a = len(text_a)
        if len_a < 50:
            continue

        for j in range(i + 1, len(listings)):
            id_b = listings[j].id
            text_b = preprocessed_texts[id_b]
            len_b = len(text_b)
            if len_b < 50:
                continue

            # Length pre-filter: skip comparison if lengths differ by more than 35%
            max_len = max(len_a, len_b)
            if abs(len_a - len_b) / max_len > 0.35:
                continue

            similarity = fuzz.token_set_ratio(text_a, text_b)
            if similarity >= 85.0:
                pair = tuple(sorted([str(id_a), str(id_b)]))
                if (pair, "TEXT_SIMILARITY") not in seen_pairs:
                    seen_pairs.add((pair, "TEXT_SIMILARITY"))
                    links_to_create.append(
                        ListingLink(
                            source_listing_id=id_a,
                            target_listing_id=id_b,
                            link_type="TEXT_SIMILARITY",
                            weight=round(similarity / 100.0, 2),
                            metadata_info={"similarity_score": round(similarity, 1)}
                        )
                    )

    if links_to_create:
        db.add_all(links_to_create)
        db.commit()

    return len(links_to_create)
