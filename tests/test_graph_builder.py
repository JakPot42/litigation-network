"""Tests for graph_builder.py — NetworkX graph construction and Plotly output."""
import pytest
from graph_builder import (
    build_networkx_graph,
    build_network_chart,
    build_allegation_chart,
    build_firm_chart,
    compute_patterns,
)


def _sample_complaints():
    return [
        {
            "id": 1,
            "case_name": "In re Alpha Corp Securities Litigation",
            "defendant_company": "Alpha Corp",
            "plaintiff_law_firm": "Firm A LLP",
            "judge_name": "Judge Smith",
            "allegation_type": "accounting_fraud",
            "industry_sector": "Technology",
            "date_filed": "2020-01-15",
            "status": "settled",
            "settlement_amount_usd": 50_000_000.0,
            "settlement_date": "2022-06-01",
            "days_to_resolution": 868,
        },
        {
            "id": 2,
            "case_name": "Beta Inc. v. Investors",
            "defendant_company": "Beta Inc.",
            "plaintiff_law_firm": "Firm B LLP",
            "judge_name": "Judge Smith",
            "allegation_type": "disclosure_failure",
            "industry_sector": "Finance",
            "date_filed": "2019-05-20",
            "status": "settled",
            "settlement_amount_usd": 100_000_000.0,
            "settlement_date": "2021-11-01",
            "days_to_resolution": 896,
        },
        {
            "id": 3,
            "case_name": "In re Gamma Corp Securities Litigation",
            "defendant_company": "Gamma Corp",
            "plaintiff_law_firm": "Firm A LLP",
            "judge_name": None,
            "allegation_type": "forward_looking_statements",
            "industry_sector": "Healthcare",
            "date_filed": "2021-03-10",
            "status": "filed",
            "settlement_amount_usd": None,
            "settlement_date": None,
            "days_to_resolution": None,
        },
    ]


# ---------------------------------------------------------------------------
# build_networkx_graph
# ---------------------------------------------------------------------------

def test_graph_has_nodes():
    G = build_networkx_graph(_sample_complaints())
    assert len(G.nodes) > 0


def test_graph_has_company_nodes():
    G = build_networkx_graph(_sample_complaints())
    company_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "company"]
    assert len(company_nodes) == 3


def test_graph_has_firm_nodes():
    G = build_networkx_graph(_sample_complaints())
    firm_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "law_firm"]
    assert len(firm_nodes) == 2  # Firm A and Firm B


def test_graph_has_judge_node():
    G = build_networkx_graph(_sample_complaints())
    judge_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "judge"]
    assert len(judge_nodes) == 1  # Judge Smith (appears in 2 cases but same node)


def test_graph_edges_firm_to_company():
    G = build_networkx_graph(_sample_complaints())
    # Firm A has 2 cases, Firm B has 1
    firm_a_id = "firm::Firm A LLP"
    assert G.has_node(firm_a_id)
    out_edges = list(G.out_edges(firm_a_id))
    assert len(out_edges) == 2


def test_graph_edge_has_allegation_type():
    G = build_networkx_graph(_sample_complaints())
    for u, v, data in G.edges(data=True):
        if data.get("edge_type") == "filed":
            assert "allegation_type" in data


def test_graph_node_labels():
    G = build_networkx_graph(_sample_complaints())
    for n, d in G.nodes(data=True):
        assert "label" in d
        assert d["label"] != ""


def test_graph_company_has_sector():
    G = build_networkx_graph(_sample_complaints())
    company_id = "company::Alpha Corp"
    assert G.nodes[company_id]["sector"] == "Technology"


def test_graph_no_judge_for_null_judge_name():
    # Gamma Corp has no judge — should not create a judge edge for it
    G = build_networkx_graph(_sample_complaints())
    # Only one judge (Judge Smith) from 2 cases — 3rd case has no judge
    judge_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "judge"]
    assert len(judge_nodes) == 1


def test_graph_empty_complaints():
    G = build_networkx_graph([])
    assert len(G.nodes) == 0
    assert len(G.edges) == 0


def test_graph_single_complaint():
    complaints = [_sample_complaints()[0]]
    G = build_networkx_graph(complaints)
    assert any(d.get("node_type") == "company" for _, d in G.nodes(data=True))
    assert any(d.get("node_type") == "law_firm" for _, d in G.nodes(data=True))


# ---------------------------------------------------------------------------
# build_network_chart
# ---------------------------------------------------------------------------

def test_network_chart_returns_traces_layout():
    result = build_network_chart(_sample_complaints())
    assert "traces" in result
    assert "layout" in result


def test_network_chart_has_scatter_traces():
    result = build_network_chart(_sample_complaints())
    types = {t.get("type") for t in result["traces"]}
    assert "scatter" in types


def test_network_chart_empty_complaints():
    result = build_network_chart([])
    assert result["traces"] == []


def test_network_chart_layout_no_axes():
    result = build_network_chart(_sample_complaints())
    xaxis = result["layout"].get("xaxis", {})
    assert xaxis.get("showticklabels") is False


# ---------------------------------------------------------------------------
# build_allegation_chart
# ---------------------------------------------------------------------------

def test_allegation_chart_returns_traces_layout():
    result = build_allegation_chart(_sample_complaints())
    assert "traces" in result
    assert "layout" in result


def test_allegation_chart_bar_type():
    result = build_allegation_chart(_sample_complaints())
    assert result["traces"][0]["type"] == "bar"


def test_allegation_chart_three_types():
    result = build_allegation_chart(_sample_complaints())
    # 3 different allegation types in sample
    assert len(result["traces"][0]["x"]) == 3


def test_allegation_chart_sorted_descending():
    result = build_allegation_chart(_sample_complaints())
    # All have count 1 so order may vary, but values should be non-increasing
    values = result["traces"][0]["y"]
    assert values == sorted(values, reverse=True)


# ---------------------------------------------------------------------------
# build_firm_chart
# ---------------------------------------------------------------------------

def test_firm_chart_returns_dict():
    result = build_firm_chart(_sample_complaints())
    assert "traces" in result
    assert result["traces"][0]["orientation"] == "h"


def test_firm_chart_firm_a_has_two_cases():
    result = build_firm_chart(_sample_complaints())
    # Firm A has 2 cases, Firm B has 1. First bar (highest) should be Firm A.
    values = result["traces"][0]["x"]
    assert values[0] == 2


# ---------------------------------------------------------------------------
# compute_patterns
# ---------------------------------------------------------------------------

def test_compute_patterns_keys():
    result = compute_patterns(_sample_complaints())
    assert "firm_industry" in result
    assert "sectors_list" in result
    assert "judge_rows" in result
    assert "industry_counts" in result
    assert "total_recovery_usd" in result
    assert "settled_count" in result


def test_compute_patterns_total_recovery():
    result = compute_patterns(_sample_complaints())
    assert result["total_recovery_usd"] == 150_000_000.0  # 50M + 100M


def test_compute_patterns_settled_count():
    result = compute_patterns(_sample_complaints())
    assert result["settled_count"] == 2


def test_compute_patterns_firm_industry_matrix():
    result = compute_patterns(_sample_complaints())
    firm_a = "Firm A LLP"
    assert firm_a in result["firm_industry"]
    # Firm A filed in Technology (Alpha Corp) and Healthcare (Gamma Corp)
    assert result["firm_industry"][firm_a]["Technology"] == 1
    assert result["firm_industry"][firm_a]["Healthcare"] == 1


def test_compute_patterns_judge_rows():
    result = compute_patterns(_sample_complaints())
    # Judge Smith has 2 cases, both settled
    judge_row = next((r for r in result["judge_rows"] if r["judge"] == "Judge Smith"), None)
    assert judge_row is not None
    assert judge_row["cases"] == 2
    assert judge_row["settled"] == 2


def test_compute_patterns_industry_counts():
    result = compute_patterns(_sample_complaints())
    assert result["industry_counts"]["Technology"] == 1
    assert result["industry_counts"]["Finance"] == 1
    assert result["industry_counts"]["Healthcare"] == 1


def test_compute_patterns_no_judge_for_null_judge():
    # Gamma Corp has no judge — Judge Smith should show 2 cases (not 3)
    result = compute_patterns(_sample_complaints())
    judge_row = next((r for r in result["judge_rows"] if r["judge"] == "Judge Smith"), None)
    assert judge_row["cases"] == 2  # only Alpha and Beta, not Gamma


def test_compute_patterns_empty():
    result = compute_patterns([])
    assert result["total_recovery_usd"] == 0
    assert result["settled_count"] == 0
    assert result["judge_rows"] == []
