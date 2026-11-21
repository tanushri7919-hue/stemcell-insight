"""
visualizations.py - Scientific visualization utilities for StemCell Insight.
Generates interactive Plotly and NetworkX diagrams for lineage trees,
differentiation pathways, molecular marker networks, protocol comparisons, and timelines.
"""

from typing import Any, Dict, List, Optional
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# Color Palette (Restrained professional biotech theme: light background, deep navy, vibrant teal, amber, coral)
COLORS = {
    "ESC": "#1E3A8A",      # Deep Navy
    "IPSC": "#0284C7",     # Sky Blue
    "MSC": "#0D9488",      # Teal
    "HSC": "#E11D48",      # Crimson Rose
    "NSC": "#7C3AED",      # Royal Purple
    "Lineage": "#64748B",  # Slate
    "Target": "#059669",   # Emerald Green
    "Signal": "#D97706",   # Amber
    "Marker": "#4F46E5",   # Indigo
    "Bg": "#F8FAFC",       # Crisp Light Gray
    "Edge": "#CBD5E1",     # Soft Silver
}


def create_lineage_network(diff_records: List[Dict[str, Any]]) -> go.Figure:
    """Build an interactive NetworkX directed graph of stem-cell lineages and target fates."""
    G = nx.DiGraph()

    for r in diff_records:
        source = r.get("source_cell_id") or "Stem Cell"
        lineage = r.get("lineage") or "Lineage"
        target = r.get("target_cell") or "Target Cell"

        G.add_node(source, type="StemCell", category=source, label=f"Source: {source}")
        G.add_node(lineage, type="Lineage", category="Lineage", label=f"Lineage: {lineage}")
        G.add_node(target, type="Target", category="Target", label=f"Target: {target}")

        G.add_edge(source, lineage, relation="specifies")
        G.add_edge(lineage, target, relation="differentiates_into")

    if len(G.nodes) == 0:
        fig = go.Figure()
        fig.update_layout(title="No lineage records available to display")
        return fig

    # Compute 2D layout using spring_layout with optimal k spacing
    pos = nx.spring_layout(G, k=0.85, seed=42)

    # Edge traces
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color=COLORS["Edge"]),
        hoverinfo="none",
        mode="lines"
    )

    # Node traces
    node_x, node_y, node_color, node_text, node_size = [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        ntype = G.nodes[node].get("type", "Other")

        if ntype == "StemCell":
            cat = G.nodes[node].get("category", "ESC")
            node_color.append(COLORS.get(cat, "#3B82F6"))
            node_size.append(32)
        elif ntype == "Lineage":
            node_color.append(COLORS["Lineage"])
            node_size.append(22)
        else:
            node_color.append(COLORS["Target"])
            node_size.append(26)

        node_text.append(f"<b>{node}</b><br>Type: {ntype}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=[n for n in G.nodes()],
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line=dict(width=2, color="#FFFFFF")
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="<b>Stem-Cell Lineage & Fate Network</b>",
        showlegend=False,
        hovermode="closest",
        margin=dict(b=20, l=20, r=20, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=550
    )
    return fig


def create_pathway_diagram(
    source_cell: str,
    target_cell: str,
    signals: List[Dict[str, Any]],
    markers: List[Dict[str, Any]]
) -> go.Figure:
    """Create an interactive biological pathway network connecting
    Signals -> Receptors/Pathways -> Transcription Factors -> Target Cell Fate.
    """
    G = nx.DiGraph()

    # Center root & target
    G.add_node(source_cell, level=0, type="Source", color="#1E3A8A")
    G.add_node(target_cell, level=3, type="Target", color="#059669")

    # Add signal nodes
    for s in signals:
        sname = s.get("signal_name", "Signal")
        pathway = s.get("pathway", "Pathway")
        role = s.get("role", "Inducer")

        color = "#D97706" if "Inducer" in role else "#DC2626"
        G.add_node(sname, level=1, type="Signal", color=color, info=f"Role: {role}<br>Pathway: {pathway}")
        G.add_edge(source_cell, sname)

        # Pathway node
        if pathway:
            G.add_node(pathway, level=2, type="Pathway", color="#6366F1", info=f"Signaling Cascade: {pathway}")
            G.add_edge(sname, pathway)
            G.add_edge(pathway, target_cell)
        else:
            G.add_edge(sname, target_cell)

    # Add marker nodes associated with target
    for m in markers[:6]:
        mname = m.get("gene_symbol") or m.get("marker_name", "Marker")
        mdesc = m.get("description", "")
        G.add_node(mname, level=4, type="Marker", color="#7C3AED", info=f"Marker: {mdesc}")
        G.add_edge(target_cell, mname)

    pos = nx.spring_layout(G, k=0.9, seed=12)

    # Edges
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color="#94A3B8"),
        hoverinfo="none",
        mode="lines"
    )

    # Nodes
    node_x, node_y, node_color, node_text, node_size = [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_color.append(G.nodes[node].get("color", "#3B82F6"))
        ntype = G.nodes[node].get("type", "Node")
        ninfo = G.nodes[node].get("info", "")

        if ntype in ("Source", "Target"):
            node_size.append(34)
        elif ntype == "Pathway":
            node_size.append(28)
        else:
            node_size.append(22)

        node_text.append(f"<b>{node}</b> ({ntype})<br>{ninfo}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=[n for n in G.nodes()],
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            color=node_color,
            size=node_size,
            line=dict(width=2, color="#FFFFFF")
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=f"<b>Differentiation Pathway: {source_cell} → {target_cell}</b>",
        showlegend=False,
        margin=dict(b=20, l=20, r=20, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#FFFFFF",
        height=520
    )
    return fig


def create_marker_profile_chart(markers: List[Dict[str, Any]]) -> go.Figure:
    """Create a categorized breakdown chart of molecular markers by biological type."""
    if not markers:
        fig = go.Figure()
        fig.update_layout(title="No markers available to plot")
        return fig

    df = pd.DataFrame(markers)
    mtypes = df["marker_type"].value_counts().reset_index()
    mtypes.columns = ["Marker Type", "Count"]

    fig = px.bar(
        mtypes,
        x="Marker Type",
        y="Count",
        color="Marker Type",
        color_discrete_sequence=["#0D9488", "#1E3A8A", "#6366F1", "#D97706", "#EC4899", "#8B5CF6"],
        title="<b>Molecular Marker Distribution by Biological Class</b>",
        text="Count"
    )
    fig.update_layout(
        showlegend=False,
        xaxis_title="<b>Marker Class</b>",
        yaxis_title="<b>Number of Curated Markers</b>",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=380
    )
    return fig


def create_protocol_timeline(steps: List[Dict[str, Any]], protocol_name: str) -> go.Figure:
    """Build a sequential step timeline for experimental differentiation protocols."""
    if not steps:
        fig = go.Figure()
        fig.update_layout(title="No steps reported for this protocol")
        return fig

    step_nums = [f"Step {s['step_number']}" for s in steps]
    procedures = [s["procedure"][:45] + "..." if len(s["procedure"]) > 45 else s["procedure"] for s in steps]
    reagents = [s.get("reagent") or "Standard Medium" for s in steps]
    durations = [s.get("duration") or "Not reported" for s in steps]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=step_nums[::-1],
        x=[1] * len(steps),
        orientation="h",
        text=[f"<b>{r}</b><br>{d} | {p}" for r, d, p in zip(reagents[::-1], durations[::-1], procedures[::-1])],
        textposition="inside",
        insidetextanchor="middle",
        marker=dict(
            color=["#0D9488", "#0284C7", "#6366F1", "#D97706", "#10B981"][:len(steps)][::-1],
            line=dict(color="#FFFFFF", width=2)
        ),
        hovertext=[f"<b>{s['procedure']}</b><br>Reagent: {s.get('reagent')}<br>Concentration: {s.get('concentration')}<br>Duration: {s.get('duration')}<br>Notes: {s.get('notes')}" for s in steps[::-1]],
        hoverinfo="text"
    ))

    fig.update_layout(
        title=f"<b>Sequential Protocol Timeline: {protocol_name}</b>",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(title="<b>Experimental Stages</b>"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=360,
        margin=dict(l=80, r=40, t=50, b=30)
    )
    return fig


def create_protocol_comparison_radar(p1: Dict[str, Any], p2: Dict[str, Any], score1: Dict[str, Any], score2: Dict[str, Any]) -> go.Figure:
    """Side-by-side radar comparison chart of protocol evidence criteria."""
    categories = [
        "Cell Line Detail",
        "Reagents & Conc.",
        "Duration Defined",
        "Markers Verified",
        "Functional Validation",
        "Efficiency Reported",
        "Literature DOI"
    ]

    vals1 = [
        100 if p1.get("source_cell") else 0,
        100 if p1.get("growth_factors") or p1.get("small_molecules") else 0,
        100 if p1.get("duration") and p1.get("duration") != "Not reported" else 0,
        100 if p1.get("validation_markers") else 0,
        100 if p1.get("functional_validation") else 0,
        100 if p1.get("reported_efficiency") and p1.get("reported_efficiency") != "Not reported" else 0,
        100 if p1.get("ref_doi") else 0
    ]

    vals2 = [
        100 if p2.get("source_cell") else 0,
        100 if p2.get("growth_factors") or p2.get("small_molecules") else 0,
        100 if p2.get("duration") and p2.get("duration") != "Not reported" else 0,
        100 if p2.get("validation_markers") else 0,
        100 if p2.get("functional_validation") else 0,
        100 if p2.get("reported_efficiency") and p2.get("reported_efficiency") != "Not reported" else 0,
        100 if p2.get("ref_doi") else 0
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=vals1 + [vals1[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=p1.get("protocol_name", "Protocol 1")[:30],
        line_color="#0D9488",
        opacity=0.6
    ))

    fig.add_trace(go.Scatterpolar(
        r=vals2 + [vals2[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=p2.get("protocol_name", "Protocol 2")[:30],
        line_color="#2563EB",
        opacity=0.6
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False
            )
        ),
        showlegend=True,
        title="<b>Reporting Completeness Comparison (Radar Profile)</b>",
        height=450,
        margin=dict(l=60, r=60, t=60, b=40)
    )
    return fig
