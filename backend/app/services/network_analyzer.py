"""
Network Analyzer Service (NetworkX).

Builds a heterogeneous graph connecting job listings and extracted contacts (phones, emails),
identifies connected components (scam syndicates), detects cross-border networks (e.g. CMR & NGA),
and updates network clusters and listing risk scores in PostgreSQL.
"""

import uuid
from typing import List, Dict, Any, Tuple, Optional, Set
import networkx as nx
from sqlalchemy.orm import Session, joinedload
from app.models.listing import Listing
from app.models.contact import Contact
from app.models.network import NetworkCluster
from app.models.signal import RiskSignal
from app.models.link import ListingLink


def build_network_graph(db: Session) -> nx.Graph:
    """
    Constructs a NetworkX graph linking job listings (annonces) and contacts (phones, emails).
    Also includes text-similarity links between listings when present.
    """
    G = nx.Graph()
    listings = db.query(Listing).options(joinedload(Listing.contacts)).all()

    for listing in listings:
        listing_node_id = f"listing_{listing.id}"
        country = (listing.country_code or "").upper().strip()
        G.add_node(
            listing_node_id,
            node_type="listing",
            id=listing.id,
            title=listing.title,
            country_code=country,
            platform=listing.platform,
            risk_score=listing.risk_score or 0
        )

        for contact in listing.contacts:
            contact_val = contact.normalized_value or contact.raw_sample or str(contact.id)
            contact_node_id = f"contact_{contact.contact_type}_{contact_val}"
            
            if not G.has_node(contact_node_id):
                G.add_node(
                    contact_node_id,
                    node_type="contact",
                    id=contact.id,
                    contact_type=contact.contact_type,
                    normalized_value=contact.normalized_value,
                    country_code=(contact.country_code or "").upper().strip()
                )

            G.add_edge(
                listing_node_id,
                contact_node_id,
                edge_type="HAS_CONTACT"
            )

    # Incorporate text similarity edges between listings if present
    similarity_links = db.query(ListingLink).filter(ListingLink.link_type == "TEXT_SIMILARITY").all()
    for link in similarity_links:
        src = f"listing_{link.source_listing_id}"
        tgt = f"listing_{link.target_listing_id}"
        if G.has_node(src) and G.has_node(tgt):
            G.add_edge(
                src,
                tgt,
                edge_type="TEXT_SIMILARITY",
                weight=link.weight
            )

    return G


def find_connected_syndicates(G: nx.Graph) -> List[Dict[str, Any]]:
    """
    Extracts connected components using nx.connected_components.
    Filters for clusters containing at least 2 listings and flags cross-border syndicates.
    """
    syndicates = []

    for component in nx.connected_components(G):
        listing_ids: List[uuid.UUID] = []
        contact_ids: Set[uuid.UUID] = set()
        countries: Set[str] = set()
        platforms: Set[str] = set()

        for node_id in component:
            node_data = G.nodes[node_id]
            if node_data.get("node_type") == "listing":
                listing_ids.append(node_data["id"])
                c = node_data.get("country_code")
                if c:
                    countries.add(c)
                p = node_data.get("platform")
                if p:
                    platforms.add(p)
            elif node_data.get("node_type") == "contact":
                cid = node_data.get("id")
                if cid:
                    contact_ids.add(cid)

        # A syndicate requires at least 2 connected listings
        if len(listing_ids) >= 2:
            sorted_countries = sorted(list(countries))
            is_cross_border = len(sorted_countries) > 1

            syndicates.append({
                "listing_ids": listing_ids,
                "contact_ids": list(contact_ids),
                "countries": sorted_countries,
                "platforms": sorted(list(platforms)),
                "is_cross_border": is_cross_border,
                # Cross-border syndicate rule: score = 100
                "risk_score": 100 if is_cross_border else None
            })

    return syndicates


def update_syndicates_and_scores(db: Session, syndicates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Persists syndicates into the `networks` (NetworkCluster) table and updates
    listings risk scores and network_id in PostgreSQL.
    Cross-border clusters receive risk_score=100 and risk_level='CRITICAL'.
    """
    # 1. Detach listings from previous networks
    db.query(Listing).update({Listing.network_id: None})
    # 2. Clear old network records
    db.query(NetworkCluster).delete()
    db.flush()

    created_clusters = 0
    cross_border_count = 0
    listings_updated = 0

    for idx, syn in enumerate(syndicates, start=1):
        member_listings = db.query(Listing).filter(Listing.id.in_(syn["listing_ids"])).all()
        if not member_listings:
            continue

        countries = syn["countries"]
        platforms = syn["platforms"]
        is_cross_border = syn["is_cross_border"]

        if is_cross_border:
            cross_border_count += 1
            risk_score = 100
            countries_tag = "-".join(countries)
            label = f"Cross-Border Syndicate #{idx} ({countries_tag} Ring)"
        else:
            # Non-cross-border syndicate: max score of listings or default 75
            max_existing = max([l.risk_score for l in member_listings], default=70)
            risk_score = max(max_existing, 70)
            countries_tag = "-".join(countries) if countries else "Local"
            label = f"Syndicate #{idx} ({countries_tag} Ring)"

        network = NetworkCluster(
            id=uuid.uuid4(),
            label=label,
            risk_score=risk_score,
            listings_count=len(member_listings),
            contacts_count=len(syn["contact_ids"]),
            countries_involved=countries,
            platforms_involved=platforms
        )
        db.add(network)
        db.flush()

        for listing in member_listings:
            listing.network_id = network.id

            if is_cross_border:
                # Set risk score to 100 for cross-border syndicates
                listing.risk_score = 100
                listing.risk_level = "CRITICAL"

                # Check or add CROSS_BORDER_SYNDICATE RiskSignal
                existing_sig = db.query(RiskSignal).filter(
                    RiskSignal.listing_id == listing.id,
                    RiskSignal.rule_code == "CROSS_BORDER_SYNDICATE"
                ).first()

                if not existing_sig:
                    db.add(RiskSignal(
                        id=uuid.uuid4(),
                        listing_id=listing.id,
                        rule_code="CROSS_BORDER_SYNDICATE",
                        severity="CRITICAL",
                        score_points=100,
                        explanation=(
                            f"Syndicat transfrontalier détecté opérant entre plusieurs pays "
                            f"({', '.join(countries)}). Score de risque maximal (100) attribué."
                        )
                    ))

            listings_updated += 1
        created_clusters += 1

    db.commit()

    return {
        "clusters_created": created_clusters,
        "cross_border_count": cross_border_count,
        "listings_updated": listings_updated
    }


def analyze_and_save_networks(db: Session) -> Dict[str, Any]:
    """
    Full pipeline:
    1. Builds listing-contact graph.
    2. Finds connected components (nx.connected_components).
    3. Detects cross-border syndicates (score=100).
    4. Updates database records (networks & listings).
    """
    G = build_network_graph(db)
    syndicates = find_connected_syndicates(G)
    stats = update_syndicates_and_scores(db, syndicates)
    return stats


def cluster_and_save_networks(db: Session) -> int:
    """Convenience alias returning count of created clusters for backward compatibility."""
    stats = analyze_and_save_networks(db)
    return stats["clusters_created"]
