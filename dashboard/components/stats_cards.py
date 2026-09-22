import streamlit as st
from typing import Dict, Any

def render_stats_cards(stats: Dict[str, Any]):
    """Renders 4 top-level KPI cards."""
    col1, col2, col3, col4 = st.columns(4)

    total_listings = stats.get("total_listings", 0)
    high_risk = stats.get("high_risk_listings", 0)
    total_networks = stats.get("total_networks", 0)
    cross_border = stats.get("cross_border_networks", 0)

    with col1:
        st.metric(label="Total Scraped Ads", value=total_listings)
    with col2:
        st.metric(label="High / Critical Risk Ads", value=high_risk, delta=f"{int(high_risk/total_listings*100) if total_listings else 0}% of ads", delta_color="inverse")
    with col3:
        st.metric(label="Syndicate Rings Detected", value=total_networks)
    with col4:
        st.metric(label="Cross-Border Rings", value=cross_border, delta="Pan-African Scope", delta_color="normal")
