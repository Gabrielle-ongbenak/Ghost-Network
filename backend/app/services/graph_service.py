import uuid
from typing import List, Dict, Any, Optional
import networkx as nx
from sqlalchemy.orm import Session
from app.models.listing import Listing
from app.models.contact import Contact
from app.models.link import ListingLink
from app.models.network import NetworkCluster
from app.schemas.graph import GraphNode, GraphEdge, GraphResponse

# Color mapping by risk level
RISK_COLOR_MAP = {
    "CRITICAL": "#E63946",  # Red
    "HIGH": "#F4A261",      # Orange
    "MEDIUM": "#E9C46A",    # Yellow
    "LOW": "#2A9D8F"        # Teal
}

from app.services.network_analyzer import cluster_and_save_networks

def build_graph_response(
    db: Session,
    network_id: Optional[uuid.UUID] = None,
    min_risk: int = 0,
    max_nodes: int = 150
) -> GraphResponse:
    """
    Constructs a graph payload with nodes and edges for Pyvis / streamlit-agraph.
    """
    query = db.query(Listing)
    if network_id:
        query = query.filter(Listing.network_id == network_id)
    if min_risk > 0:
        query = query.filter(Listing.risk_score >= min_risk)

    listings = query.limit(max_nodes).all()
    listing_ids = {l.id for l in listings}

    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []
    seen_nodes = set()
    seen_edges = set()

    # 1. Add Listing Nodes
    for l in listings:
        node_id = f"listing_{str(l.id)[:8]}"
        color = RISK_COLOR_MAP.get(l.risk_level, "#2A9D8F")
        tooltip = (
            f"<b>{l.title}</b><br/>"
            f"Platform: {l.platform.upper()} | Country: {l.country_code}<br/>"
            f"Risk Score: <b>{l.risk_score}/100 ({l.risk_level})</b><br/>"
            f"Poster: {l.poster_name or 'Unknown'}"
        )
        nodes.append(
            GraphNode(
                id=node_id,
                label=f"[{l.country_code}] {l.title[:24]}...",
                group="listing",
                country=l.country_code,
                risk_score=l.risk_score,
                color=color,
                size=22 if l.risk_score < 70 else 28,
                title=tooltip
            )
        )
        seen_nodes.add(str(l.id))

    # 2. Add Contact Nodes and direct Listing -> Contact edges
    for l in listings:
        l_node_id = f"listing_{str(l.id)[:8]}"
        for c in l.contacts:
            c_node_id = f"contact_{c.normalized_value}"
            if c_node_id not in seen_nodes:
                seen_nodes.add(c_node_id)
                nodes.append(
                    GraphNode(
                        id=c_node_id,
                        label=c.normalized_value,
                        group="contact",
                        country=c.country_code,
                        risk_score=85 if c.listings_count >= 2 else 40,
                        color="#457B9D" if c.contact_type == "EMAIL" else "#F4A261",
                        size=30 if c.listings_count >= 2 else 20,
                        title=f"{c.contact_type}: {c.normalized_value}<br/>Linked across {c.listings_count} listings"
                    )
                )

            edge_key = (l_node_id, c_node_id)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append(
                    GraphEdge(
                        source=l_node_id,
                        target=c_node_id,
                        label="contact",
                        link_type="ADVERTISES",
                        weight=1.0,
                        color="#A8DADC",
                        width=2,
                        title=f"Listed in {l.title[:30]}"
                    )
                )

    # 3. Add explicit Listing-to-Listing similarity edges
    links = db.query(ListingLink).filter(
        ListingLink.source_listing_id.in_(listing_ids),
        ListingLink.target_listing_id.in_(listing_ids)
    ).all()

    for link in links:
        src_node = f"listing_{str(link.source_listing_id)[:8]}"
        tgt_node = f"listing_{str(link.target_listing_id)[:8]}"
        edge_key = tuple(sorted([src_node, tgt_node]))
        if edge_key not in seen_edges:
            seen_edges.add(edge_key)
            edges.append(
                GraphEdge(
                    source=src_node,
                    target=tgt_node,
                    label=f"{int(link.weight * 100)}% match" if link.link_type == "TEXT_SIMILARITY" else link.link_type,
                    link_type=link.link_type,
                    weight=link.weight,
                    color="#E63946" if link.link_type == "TEXT_SIMILARITY" else "#F4A261",
                    width=3 if link.weight > 0.8 else 1,
                    title=f"Connection: {link.link_type} (weight: {link.weight})"
                )
            )

    return GraphResponse(nodes=nodes, edges=edges)
