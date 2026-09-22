import streamlit as st
import pandas as pd
from typing import Dict, Any, List

def render_listing_table(listings_data: Dict[str, Any]) -> str:
    """
    Renders a table of listings with risk badges and returns the selected listing ID.
    """
    items: List[Dict[str, Any]] = listings_data.get("items", [])
    if not items:
        st.info("No listings found matching current criteria.")
        return None

    # Format into DataFrame for clear display
    rows = []
    for item in items:
        rows.append({
            "ID": item["id"],
            "Title": item["title"],
            "Country": item["country_code"],
            "Platform": item["platform"].upper(),
            "Risk Score": f"{item['risk_score']} ({item['risk_level']})",
            "Contacts": ", ".join(item.get("contacts_summary", [])) or "None",
            "Signals": item.get("detected_signals_count", 0)
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df[["Title", "Country", "Platform", "Risk Score", "Contacts", "Signals"]],
        use_container_width=True,
        hide_index=True
    )

    # Selector to inspect a listing
    listing_options = {f"[{it['country_code']}] {it['title']} (Risk: {it['risk_score']})": it["id"] for it in items}
    selected_label = st.selectbox("Select a listing to inspect risk signals and syndicate links:", options=list(listing_options.keys()))
    return listing_options[selected_label] if selected_label else None
