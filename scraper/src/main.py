"""
Pan-African Job Scam & Threat Network Detector - Apify Actor.
Designed for the Apify x SCA BuildHer 2026 Hackathon (Theme: Ship and Earn Africa).

Monetization Model: Pay-Per-Event (PPE)
- LISTING_SCANNED: $0.005 per listing parsed and audited.
- SYNDICATE_UNMASKED: $0.05 per cross-border fraud syndicate unmasked.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from apify import Actor

from src.extractor import extract_contacts, infer_country_code, analyze_listing_risk
from src.network import build_network_and_find_syndicates
from src.data_loader import get_target_listings


async def main():
    async with Actor:
        Actor.log.info("🚀 Ghost Networks: Pan-African Job Scam & Threat Network Detector initialized.")

        # 1. Read input configuration from Apify
        actor_input: Dict[str, Any] = await Actor.get_input() or {}
        target_countries = actor_input.get("target_countries", ["CMR", "NGA", "KEN"])
        search_keywords = actor_input.get("search_keywords", ["assistant", "receptionist", "secretary", "cashier", "supervisor"])
        max_listings = int(actor_input.get("max_listings", 30))
        enable_network_analysis = bool(actor_input.get("enable_network_analysis", True))
        custom_listings = actor_input.get("custom_listings", [])

        Actor.log.info(
            f"Config: Countries={target_countries} | Keywords={len(search_keywords)} | "
            f"Max={max_listings} | NetworkX={enable_network_analysis}"
        )

        # 2. Retrieve job postings (live, seed archive, or custom user batch)
        raw_listings = get_target_listings(
            target_countries=target_countries,
            search_keywords=search_keywords,
            max_listings=max_listings,
            custom_listings=custom_listings
        )
        Actor.log.info(f"Retrieved {len(raw_listings)} listings for inspection.")

        analyzed_listings: List[Dict[str, Any]] = []
        total_contacts_extracted = 0

        # 3. Process each listing & charge PPE event
        for raw_item in raw_listings:
            title = str(raw_item.get("title") or "Job Advertisement").strip()
            description = str(raw_item.get("description") or "").strip()
            source_id = str(raw_item.get("source_id") or f"ad_{len(analyzed_listings)+1}")
            platform = str(raw_item.get("platform") or "classifieds").strip()
            source_url = str(raw_item.get("source_url") or "https://example.com")
            poster_name = raw_item.get("poster_name")

            # Extract contacts via regex & phonenumbers E.164 normalization
            initial_country = str(raw_item.get("country_code") or raw_item.get("country") or "CMR")
            contacts = extract_contacts(f"{title}\n{description}", default_country=initial_country)

            # Merge any explicit contacts passed in input
            for explicit in raw_item.get("extracted_contacts", []):
                val = explicit.get("raw_value") or explicit.get("raw")
                t = explicit.get("contact_type") or explicit.get("type", "PHONE")
                if val and not any(c.get("normalized") == val or c.get("raw") == val for c in contacts):
                    contacts.append({"type": t, "raw": val, "normalized": val, "country": initial_country})

            # Refine country code
            country_code = infer_country_code(raw_item, contacts)

            # Analyze individual scam risk signals
            risk_analysis = analyze_listing_risk(title, description, contacts, country_code)

            listing_record = {
                "record_type": "JOB_LISTING",
                "listing_id": source_id,
                "source_id": source_id,
                "title": title,
                "description": description,
                "platform": platform,
                "country": country_code,
                "country_code": country_code,
                "poster_name": poster_name,
                "source_url": source_url,
                "contacts": contacts,
                "risk_score": risk_analysis["risk_score"],
                "risk_level": risk_analysis["risk_level"],
                "risk_signals": risk_analysis["risk_signals"],
                "is_fraud_suspect": "YES" if risk_analysis["risk_score"] >= 70 else "NO",
                "syndicate_id": None,
                "syndicate_label": None,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            analyzed_listings.append(listing_record)
            total_contacts_extracted += len(contacts)

            # --- Pay-Per-Event (PPE) Monetization ---
            # Charge per individual listing scanned & audited
            try:
                await Actor.charge("LISTING_SCANNED")
            except Exception as charge_err:
                Actor.log.warning(f"Actor.charge('LISTING_SCANNED') notice: {charge_err}")

        # 4. NetworkX Graph Analysis & Cross-Border Syndicate Detection
        syndicates_detected = []
        cross_border_syndicates_count = 0

        if enable_network_analysis and analyzed_listings:
            Actor.log.info("🕸️ Running NetworkX correlation analysis to unmask criminal syndicates...")
            analysis_result = build_network_and_find_syndicates(analyzed_listings)
            syndicates_detected = analysis_result["syndicates"]
            cross_border_syndicates_count = analysis_result["cross_border_count"]

            Actor.log.info(
                f"Identified {len(syndicates_detected)} syndicates, including "
                f"{cross_border_syndicates_count} cross-border rings."
            )

            # Charge PPE for each high-impact cross-border syndicate unmasked
            for syn in syndicates_detected:
                if syn.get("is_cross_border"):
                    try:
                        await Actor.charge("SYNDICATE_UNMASKED")
                    except Exception as charge_err:
                        Actor.log.warning(f"Actor.charge('SYNDICATE_UNMASKED') notice: {charge_err}")

        # 5. Push results to Apify Dataset
        Actor.log.info(f"Saving {len(analyzed_listings)} listings to Apify default dataset...")
        for listing in analyzed_listings:
            await Actor.push_data(listing)

        # Also push detected syndicates as discrete dataset records
        for syn in syndicates_detected:
            syn_record = {
                "record_type": "SYNDICATE_ALERT",
                **syn,
                "timestamp": datetime.utcnow().isoformat()
            }
            await Actor.push_data(syn_record)

        # 6. Save Executive Summary to Key-Value Store OUTPUT
        executive_summary = {
            "title": "Pan-African Job Scam & Threat Network Detector - Audit Report",
            "execution_time": datetime.utcnow().isoformat(),
            "target_countries": target_countries,
            "total_listings_scanned": len(analyzed_listings),
            "total_contacts_extracted": total_contacts_extracted,
            "high_risk_listings": len([l for l in analyzed_listings if l["risk_score"] >= 70]),
            "syndicates_unmasked": len(syndicates_detected),
            "cross_border_syndicates": cross_border_syndicates_count,
            "syndicate_details": [
                {
                    "label": s["label"],
                    "risk_score": s["risk_score"],
                    "countries": s["countries_involved"],
                    "listings_count": s["listings_count"],
                    "shared_contacts": [c["value"] for c in s["shared_contacts"]]
                }
                for s in syndicates_detected
            ]
        }
        await Actor.set_value("OUTPUT", executive_summary)

        Actor.log.info("✅ Actor run completed successfully. Executive report saved to OUTPUT.")


if __name__ == "__main__":
    asyncio.run(main())
