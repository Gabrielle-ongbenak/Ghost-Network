import streamlit as st
import plotly.express as px
from api_client import client
from components.stats_cards import render_stats_cards
from components.graph_view import render_network_graph
from components.listing_table import render_listing_table
from components.listing_modal import render_listing_modal
from components.filters import render_sidebar_filters

# Page Configuration
st.set_page_config(
    page_title="Ghost Networks | Pan-African Job-Scam Detection",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("🕸️ Ghost Networks")
st.caption("Cross-Border Job-Scam Syndicate Detection Across Africa • Apify x She Code Africa Hackathon")

# Fetch high-level statistics
stats = client.get_stats()
if not stats:
    st.error("⚠️ Backend API connection unavailable. Please check that FastAPI is running on port 8000.")
    st.stop()

# 1. KPI Metric Cards
render_stats_cards(stats)
st.write("")

# Sidebar Filters
filters = render_sidebar_filters()

# Trigger detection button in sidebar
if st.sidebar.button("🔄 Re-run Detection Pipeline"):
    with st.spinner("Analyzing text similarity, contacts, and clustering syndicates..."):
        res = client.run_detection()
        if res:
            st.sidebar.success(f"Updated! {res.get('syndicates_identified', 0)} syndicates clustered.")
            st.rerun()

# Syndicates selection
syndicates = client.get_networks()
syndicate_options = {"All Syndicates": None}
for s in syndicates:
    syndicate_options[f"{s['label']} ({s['listings_count']} ads, Risk: {s['risk_score']})"] = str(s["id"])

selected_syndicate_label = st.sidebar.selectbox("Syndicate Focus", options=list(syndicate_options.keys()))
selected_network_id = syndicate_options[selected_syndicate_label]

# Main Content Tabs
tab_graph, tab_listings, tab_analytics = st.tabs([
    "🕸️ Syndicate Network Graph",
    "📋 Scraped Ads & Risk Breakdown",
    "📊 Cross-Border Analytics"
])

with tab_graph:
    st.markdown("#### Interactive Syndicate Graph")
    st.caption("Visualizing shared contacts (diamonds) and recycled text templates linking ads (circles) across platforms and borders.")

    graph_data = client.get_graph(
        network_id=selected_network_id,
        min_risk=filters["min_risk"],
        max_nodes=150
    )
    if graph_data:
        render_network_graph(graph_data, height="620px")
    else:
        st.info("No network nodes match current filters.")

with tab_listings:
    st.markdown("#### Scraped Job Listings")
    listings_data = client.get_listings(
        country=filters["country"],
        platform=filters["platform"],
        min_risk=filters["min_risk"],
        network_id=selected_network_id,
        page=1,
        page_size=50
    )

    if listings_data:
        selected_listing_id = render_listing_table(listings_data)
        if selected_listing_id:
            st.write("---")
            detail = client.get_listing_detail(selected_listing_id)
            if detail:
                render_listing_modal(detail)

with tab_analytics:
    st.markdown("#### Multi-Country & Multi-Platform Intelligence")
    col_chart1, col_chart2 = st.columns(2)

    country_data = stats.get("country_breakdown", {})
    if country_data:
        fig_country = px.bar(
            x=list(country_data.keys()),
            y=list(country_data.values()),
            labels={"x": "Country Code", "y": "Number of Listings"},
            title="Listings Scraped by Country",
            color=list(country_data.keys()),
            color_discrete_sequence=["#E63946", "#F4A261", "#2A9D8F"]
        )
        fig_country.update_layout(template="plotly_dark", showlegend=False)
        col_chart1.plotly_chart(fig_country, use_container_width=True)

    platform_data = stats.get("platform_breakdown", {})
    if platform_data:
        fig_platform = px.pie(
            names=list(platform_data.keys()),
            values=list(platform_data.values()),
            title="Distribution by Scraped Platform",
            hole=0.4,
            color_discrete_sequence=["#457B9D", "#E76F51", "#2A9D8F", "#E9C46A"]
        )
        fig_platform.update_layout(template="plotly_dark")
        col_chart2.plotly_chart(fig_platform, use_container_width=True)

    st.markdown("#### Top Reused Scam Contacts")
    top_contacts = stats.get("top_scam_contacts", [])
    if top_contacts:
        contact_rows = []
        for tc in top_contacts:
            contact_rows.append({
                "Contact": tc["normalized_value"],
                "Type": tc["contact_type"],
                "Ads Count": tc["listings_count"],
                "Countries Active": ", ".join(tc["countries"])
            })
        st.table(contact_rows)
