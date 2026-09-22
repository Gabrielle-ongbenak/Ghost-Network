import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from typing import Dict, Any

def render_network_graph(graph_data: Dict[str, Any], height: str = "600px"):
    """
    Renders an interactive Pyvis graph inside Streamlit.
    """
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        st.info("No network connections match the selected filters.")
        return

    net = Network(height=height, width="100%", bgcolor="#0E1117", font_color="#FFFFFF")

    # Configure physics for smooth layout
    net.set_options("""
    {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -4000,
          "centralGravity": 0.3,
          "springLength": 95,
          "springConstant": 0.04,
          "damping": 0.09,
          "avoidOverlap": 0.1
        },
        "minVelocity": 0.75
      },
      "nodes": {
        "borderWidth": 2,
        "borderWidthSelected": 4,
        "font": {
          "size": 13,
          "color": "#FFFFFF"
        }
      },
      "edges": {
        "smooth": {
          "type": "continuous"
        }
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "zoomView": true
      }
    }
    """)

    for n in nodes:
        shape = "dot" if n.get("group") == "listing" else "diamond"
        net.add_node(
            n_id=n["id"],
            label=n["label"],
            title=n.get("title", ""),
            color=n.get("color", "#2A9D8F"),
            size=n.get("size", 20),
            shape=shape
        )

    for e in edges:
        net.add_edge(
            source=e["from"],
            to=e["to"],
            label=e.get("label", ""),
            title=e.get("title", ""),
            color=e.get("color", "#888888"),
            width=e.get("width", 1)
        )

    html_content = net.generate_html()
    components.html(html_content, height=620, scrolling=False)
