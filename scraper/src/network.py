"""
NetworkX Graph & Cross-Border Scam Syndicate Analyzer.
Builds a correlation graph linking job listings and extracted contacts (phones, emails).
Identifies connected components and flags multi-country criminal syndicates.
"""

from typing import List, Dict, Any, Set
import networkx as nx


def build_network_and_find_syndicates(listings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Constructs a NetworkX bipartite graph (Listings <-> Contacts),
    finds connected components, and unmasks cross-border syndicates.
    """
    G = nx.Graph()

    # 1. Build Graph
    for l in listings:
        l_id = str(l.get("source_id") or l.get("id"))
        G.add_node(
            f"listing_{l_id}",
            node_type="listing",
            data=l
        )

        for c in l.get("contacts", []):
            c_val = c.get("normalized") or c.get("raw")
            c_node_id = f"contact_{c.get('type')}_{c_val}"
            
            if not G.has_node(c_node_id):
                G.add_node(
                    c_node_id,
                    node_type="contact",
                    contact_type=c.get("type"),
                    value=c_val,
                    country=c.get("country")
                )

            G.add_edge(f"listing_{l_id}", c_node_id)

    # 2. Find Connected Components
    syndicates = []
    cross_border_count = 0
    listings_by_id = {str(l.get("source_id") or l.get("id")): l for l in listings}

    for idx, component in enumerate(nx.connected_components(G), start=1):
        member_listing_ids = []
        shared_contacts = []
        countries = set()
        platforms = set()

        for node_id in component:
            node = G.nodes[node_id]
            if node.get("node_type") == "listing":
                l_data = node.get("data", {})
                lid = str(l_data.get("source_id") or l_data.get("id"))
                member_listing_ids.append(lid)
                c_code = l_data.get("country_code")
                if c_code:
                    countries.add(c_code)
                plat = l_data.get("platform")
                if plat:
                    platforms.add(plat)
            elif node.get("node_type") == "contact":
                shared_contacts.append({
                    "type": node.get("contact_type"),
                    "value": node.get("value"),
                    "country": node.get("country")
                })

        # A syndicate consists of at least 2 connected listings sharing identifiers
        if len(member_listing_ids) >= 2:
            sorted_countries = sorted(list(countries))
            is_cross_border = len(sorted_countries) > 1

            if is_cross_border:
                cross_border_count += 1
                risk_score = 100
                label = f"Cross-Border Syndicate #{idx} ({'-'.join(sorted_countries)} Ring)"
            else:
                risk_score = 75
                country_tag = sorted_countries[0] if sorted_countries else "Local"
                label = f"Syndicate #{idx} ({country_tag} Ring)"

            syndicate_info = {
                "syndicate_id": f"syn_{idx:03d}",
                "label": label,
                "risk_score": risk_score,
                "is_cross_border": is_cross_border,
                "listings_count": len(member_listing_ids),
                "contacts_count": len(shared_contacts),
                "countries_involved": sorted_countries,
                "platforms_involved": sorted(list(platforms)),
                "member_listing_ids": member_listing_ids,
                "shared_contacts": shared_contacts
            }
            syndicates.append(syndicate_info)

            # Update member listings with syndicate metadata & 100 score if cross-border
            for lid in member_listing_ids:
                if lid in listings_by_id:
                    target_l = listings_by_id[lid]
                    target_l["syndicate_id"] = syndicate_info["syndicate_id"]
                    target_l["syndicate_label"] = label
                    if is_cross_border:
                        target_l["risk_score"] = 100
                        target_l["risk_level"] = "CRITICAL"
                        target_l["is_fraud_suspect"] = "YES"
                        # Append cross-border signal if not already present
                        signals = target_l.setdefault("risk_signals", [])
                        if not any(s.get("code") == "CROSS_BORDER_SYNDICATE" for s in signals):
                            signals.append({
                                "code": "CROSS_BORDER_SYNDICATE",
                                "points": 100,
                                "description": f"Membre d'un syndicat d'arnaque transfrontalier opérant entre {', '.join(sorted_countries)}"
                            })

    return {
        "syndicates": syndicates,
        "total_syndicates": len(syndicates),
        "cross_border_count": cross_border_count
    }
