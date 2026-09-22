import streamlit as st
from typing import Dict, Any

def render_listing_modal(detail: Dict[str, Any]):
    """
    Renders an in-depth view of a job listing with plain-English explainable risk signals.
    """
    st.subheader(detail.get("title", "Job Listing Details"))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Country:** `{detail.get('country_code')}`")
        st.markdown(f"**Platform:** `{detail.get('platform', '').upper()}`")
    with col2:
        risk_score = detail.get("risk_score", 0)
        risk_level = detail.get("risk_level", "LOW")
        color = "#E63946" if risk_score >= 80 else ("#F4A261" if risk_score >= 60 else "#2A9D8F")
        st.markdown(f"**Risk Score:** <span style='color:{color}; font-weight:bold; font-size:18px;'>{risk_score}/100 ({risk_level})</span>", unsafe_allow_html=True)
        st.markdown(f"**Poster:** `{detail.get('poster_name') or 'Anonymous'}`")
    with col3:
        st.markdown(f"[🔗 View Original Ad]({detail.get('source_url')})")

    st.divider()

    # Plain-English one-line explanation
    summary = detail.get("one_line_summary", "")
    if summary:
        if "CRITICAL" in summary or "HIGH" in summary:
            st.error(summary)
        elif "MEDIUM" in summary:
            st.warning(summary)
        else:
            st.success(summary)

    # Detailed Signals Breakdown
    signals = detail.get("signals", [])
    if signals:
        st.markdown("### 🔍 Detected Risk Signals")
        for s in signals:
            points = s.get("score_points", 0)
            st.markdown(f"- **+{points} pts** | `{s.get('rule_code')}`: {s.get('explanation')}")

    # Connected Scam Contacts
    contacts = detail.get("contacts", [])
    if contacts:
        st.markdown("### 📞 Associated Contacts")
        cols = st.columns(len(contacts)) if len(contacts) <= 3 else st.columns(3)
        for i, c in enumerate(contacts):
            with cols[i % 3]:
                st.markdown(f"- **{c.get('contact_type')}:** `{c.get('normalized_value')}` (Appears in {c.get('listings_count')} ads)")

    # Linked Listings in the Syndicate
    linked = detail.get("linked_listings", [])
    if linked:
        st.markdown("### 🕸️ Connected Listings in Syndicate Network")
        for item in linked:
            st.markdown(f"- **[{item.get('country_code')}] {item.get('title')}** (`{item.get('platform')}`) — *{item.get('evidence')}*")

    st.markdown("### 📄 Job Description")
    st.text_area("", value=detail.get("description", ""), height=120, disabled=True)
