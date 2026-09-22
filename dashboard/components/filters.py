import streamlit as st
from typing import Dict, Any

def render_sidebar_filters() -> Dict[str, Any]:
    """Renders dashboard filter controls in the sidebar."""
    st.sidebar.header("🔍 Filter & Network Scope")

    country = st.sidebar.selectbox("Country", options=["ALL", "CMR", "NGA", "KEN"], index=0)
    platform = st.sidebar.selectbox("Platform", options=["ALL", "jiji", "jobberman", "facebook_group", "cameroon_classifieds"], index=0)
    min_risk = st.sidebar.slider("Minimum Risk Score", min_value=0, max_value=100, value=0, step=5)

    return {
        "country": country if country != "ALL" else None,
        "platform": platform if platform != "ALL" else None,
        "min_risk": min_risk
    }
