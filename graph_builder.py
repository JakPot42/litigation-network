"""
Builds and renders the securities litigation network graph.

Nodes: defendant companies, plaintiff law firms, judges.
Edges: law_firm → company (filed complaint), judge → company (presided).
Edge color encodes allegation type.

Returns Plotly JSON for client-side rendering via CDN.
"""
import json
import networkx as nx
from config import ALLEGATION_COLORS, SECTOR_COLORS, ALLEGATION_LABELS


_FIRM_COLOR = "#4a4e69"
_JUDGE_COLOR = "#6c757d"
_EDGE_JUDGE_COLOR = "#adb5bd"


def build_networkx_graph(complaints: list[dict]) -> nx.DiGraph:
    G = nx.DiGraph()

    # Track case counts per node for sizing
    company_counts: dict[str, int] = {}
    firm_counts: dict[str, int] = {}
    judge_counts: dict[str, int] = {}

    for c in complaints:
        company = c["defendant_company"]
        firm = c["plaintiff_law_firm"]
        judge = c.get("judge_name") or ""
        sector = c.get("industry_sector", "Other")
        allegation = c.get("allegation_type", "disclosure_failure")
        case_name = c.get("case_name", "")
        date_filed = c.get("date_filed", "")

        company_id = f"company::{company}"
        firm_id = f"firm::{firm}"

        company_counts[company_id] = company_counts.get(company_id, 0) + 1
        firm_counts[firm_id] = firm_counts.get(firm_id, 0) + 1

        if not G.has_node(company_id):
            G.add_node(company_id, node_type="company", label=company,
                       sector=sector, color=SECTOR_COLORS.get(sector, "#6c757d"))
        if not G.has_node(firm_id):
            G.add_node(firm_id, node_type="law_firm", label=firm, color=_FIRM_COLOR)

        G.add_edge(firm_id, company_id,
                   edge_type="filed",
                   allegation_type=allegation,
                   case_name=case_name,
                   date_filed=date_filed)

        if judge:
            judge_id = f"judge::{judge}"
            judge_counts[judge_id] = judge_counts.get(judge_id, 0) + 1
            if not G.has_node(judge_id):
                G.add_node(judge_id, node_type="judge", label=judge, color=_JUDGE_COLOR)
            if not G.has_edge(judge_id, company_id):
                G.add_edge(judge_id, company_id, edge_type="presided",
                           allegation_type=allegation, case_name=case_name)

    # Store case counts on nodes for size scaling
    for nid, count in company_counts.items():
        if G.has_node(nid):
            G.nodes[nid]["case_count"] = count
    for nid, count in firm_counts.items():
        if G.has_node(nid):
            G.nodes[nid]["case_count"] = count
    for nid, count in judge_counts.items():
        if G.has_node(nid):
            G.nodes[nid]["case_count"] = count

    return G


def build_network_chart(complaints: list[dict]) -> dict:
    """Build Plotly network graph. Returns {traces, layout}."""
    if not complaints:
        return {"traces": [], "layout": {"title": "No cases loaded"}}

    G = build_networkx_graph(complaints)
    if len(G.nodes) == 0:
        return {"traces": [], "layout": {"title": "No graph data"}}

    pos = nx.spring_layout(G, seed=42, k=2.5)

    traces = []

    # Edge traces grouped by allegation type (filed edges) + judge edges
    filed_by_type: dict[str, list] = {}
    judge_edges_xy = ([], [])

    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        if data.get("edge_type") == "presided":
            judge_edges_xy[0].extend([x0, x1, None])
            judge_edges_xy[1].extend([y0, y1, None])
        else:
            atype = data.get("allegation_type", "disclosure_failure")
            if atype not in filed_by_type:
                filed_by_type[atype] = ([], [])
            filed_by_type[atype][0].extend([x0, x1, None])
            filed_by_type[atype][1].extend([y0, y1, None])

    for atype, (ex, ey) in filed_by_type.items():
        traces.append({
            "type": "scatter", "mode": "lines",
            "x": ex, "y": ey,
            "line": {"width": 1.5, "color": ALLEGATION_COLORS.get(atype, "#999")},
            "name": ALLEGATION_LABELS.get(atype, atype),
            "hoverinfo": "none",
            "legendgroup": atype,
        })

    if judge_edges_xy[0]:
        traces.append({
            "type": "scatter", "mode": "lines",
            "x": judge_edges_xy[0], "y": judge_edges_xy[1],
            "line": {"width": 0.8, "color": _EDGE_JUDGE_COLOR, "dash": "dot"},
            "name": "Presided (judge)",
            "hoverinfo": "none",
        })

    # Node traces by type
    for node_type, marker_symbol, size_base in [
        ("company", "circle", 18),
        ("law_firm", "diamond", 16),
        ("judge", "square", 12),
    ]:
        nodes = [(n, d) for n, d in G.nodes(data=True) if d.get("node_type") == node_type]
        if not nodes:
            continue
        node_ids, node_data = zip(*nodes)
        xs = [pos[n][0] for n in node_ids]
        ys = [pos[n][1] for n in node_ids]
        colors = [d.get("color", "#999") for d in node_data]
        labels = [d.get("label", n) for n, d in zip(node_ids, node_data)]
        sizes = [size_base + min(d.get("case_count", 1) * 4, 20) for d in node_data]
        hover = [f"<b>{d.get('label', '')}</b><br>Type: {node_type.replace('_', ' ').title()}"
                 + (f"<br>Sector: {d.get('sector', '')}" if node_type == "company" else "")
                 + f"<br>Cases: {d.get('case_count', 1)}"
                 for d in node_data]

        type_label = {"company": "Defendant Company", "law_firm": "Plaintiff Firm", "judge": "Presiding Judge"}[node_type]
        traces.append({
            "type": "scatter", "mode": "markers+text",
            "x": xs, "y": ys,
            "text": labels,
            "textposition": "top center",
            "textfont": {"size": 9},
            "marker": {
                "size": sizes,
                "color": colors,
                "symbol": marker_symbol,
                "line": {"width": 1.5, "color": "#fff"},
            },
            "hovertext": hover,
            "hoverinfo": "text",
            "name": type_label,
        })

    layout = {
        "title": "Securities Litigation Network",
        "showlegend": True,
        "legend": {"x": 0, "y": 1, "bgcolor": "rgba(255,255,255,0.8)"},
        "hovermode": "closest",
        "xaxis": {"showgrid": False, "zeroline": False, "showticklabels": False},
        "yaxis": {"showgrid": False, "zeroline": False, "showticklabels": False},
        "height": 540,
        "paper_bgcolor": "#f8f9fa",
        "plot_bgcolor": "#f8f9fa",
        "margin": {"l": 20, "r": 20, "t": 50, "b": 20},
        "font": {"family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"},
    }
    return {"traces": traces, "layout": layout}


def build_allegation_chart(complaints: list[dict]) -> dict:
    """Bar chart of allegation type counts."""
    counts: dict[str, int] = {}
    for c in complaints:
        a = c.get("allegation_type", "other")
        counts[a] = counts.get(a, 0) + 1
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    labels = [ALLEGATION_LABELS.get(k, k) for k, _ in sorted_items]
    values = [v for _, v in sorted_items]
    colors = [ALLEGATION_COLORS.get(k, "#999") for k, _ in sorted_items]
    traces = [{"type": "bar", "x": labels, "y": values, "marker": {"color": colors},
               "hovertemplate": "<b>%{x}</b><br>Cases: %{y}<extra></extra>"}]
    layout = {
        "title": "Allegation Type Distribution",
        "xaxis": {"title": "Allegation Category"},
        "yaxis": {"title": "Number of Cases"},
        "height": 320,
        "paper_bgcolor": "#f8f9fa",
        "plot_bgcolor": "#f8f9fa",
        "margin": {"l": 50, "r": 20, "t": 50, "b": 100},
        "xaxis_tickangle": -25,
        "font": {"family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"},
    }
    return {"traces": traces, "layout": layout}


def build_firm_chart(complaints: list[dict]) -> dict:
    """Bar chart of most active plaintiff law firms."""
    counts: dict[str, int] = {}
    for c in complaints:
        f = c.get("plaintiff_law_firm", "Unknown")
        counts[f] = counts.get(f, 0) + 1
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    labels = [k.split(" LLP")[0].split(" LLC")[0] for k, _ in sorted_items]
    values = [v for _, v in sorted_items]
    traces = [{
        "type": "bar", "y": labels, "x": values, "orientation": "h",
        "marker": {"color": _FIRM_COLOR},
        "hovertemplate": "<b>%{y}</b><br>Cases filed: %{x}<extra></extra>",
    }]
    layout = {
        "title": "Most Active Plaintiff Firms",
        "xaxis": {"title": "Cases filed"},
        "yaxis": {"autorange": "reversed"},
        "height": max(280, 50 * len(labels) + 80),
        "paper_bgcolor": "#f8f9fa",
        "plot_bgcolor": "#f8f9fa",
        "margin": {"l": 240, "r": 20, "t": 50, "b": 50},
        "font": {"family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"},
    }
    return {"traces": traces, "layout": layout}


def compute_patterns(complaints: list[dict]) -> dict:
    """Compute all pattern analysis data for the patterns page."""
    # Firm × industry table
    firm_industry: dict[str, dict[str, int]] = {}
    sectors: set[str] = set()
    for c in complaints:
        firm = c.get("plaintiff_law_firm", "")
        sector = c.get("industry_sector", "Other")
        sectors.add(sector)
        if firm not in firm_industry:
            firm_industry[firm] = {}
        firm_industry[firm][sector] = firm_industry[firm].get(sector, 0) + 1

    # Judge resolution stats
    judge_stats: dict[str, dict] = {}
    for c in complaints:
        judge = c.get("judge_name") or ""
        if not judge:
            continue
        if judge not in judge_stats:
            judge_stats[judge] = {"cases": 0, "settled": 0, "total_days": 0, "total_recovery": 0.0}
        judge_stats[judge]["cases"] += 1
        if c.get("status") == "settled":
            judge_stats[judge]["settled"] += 1
            if c.get("days_to_resolution"):
                judge_stats[judge]["total_days"] += c["days_to_resolution"]
            if c.get("settlement_amount_usd"):
                judge_stats[judge]["total_recovery"] += c["settlement_amount_usd"]

    judge_rows = []
    for judge, s in sorted(judge_stats.items(), key=lambda x: x[1]["cases"], reverse=True):
        settled = s["settled"]
        avg_days = (s["total_days"] // settled) if settled > 0 and s["total_days"] > 0 else None
        total_rec = s["total_recovery"]
        judge_rows.append({
            "judge": judge,
            "cases": s["cases"],
            "settled": settled,
            "avg_days": avg_days,
            "total_recovery_usd": total_rec,
        })

    # Industry distribution
    industry_counts: dict[str, int] = {}
    for c in complaints:
        sec = c.get("industry_sector", "Other")
        industry_counts[sec] = industry_counts.get(sec, 0) + 1

    # Settlement stats
    settled = [c for c in complaints if c.get("status") == "settled" and c.get("settlement_amount_usd")]
    total_recovery = sum(c["settlement_amount_usd"] for c in settled)

    return {
        "firm_industry": firm_industry,
        "sectors_list": sorted(sectors),
        "judge_rows": judge_rows,
        "industry_counts": industry_counts,
        "total_recovery_usd": total_recovery,
        "settled_count": len(settled),
    }
