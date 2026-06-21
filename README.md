# Securities Class Action Litigation Network

Interactive network graph of securities class action litigation — Claude extracts allegation types and harm theories from complaint text, NetworkX builds the graph of plaintiff firms, defendant companies, and judges, and Plotly renders it as an interactive visualization.

Built for legal analysts and researchers who want to see patterns across securities litigation that don't surface from reading individual cases.

**Live demo:** https://litigation-network.onrender.com

---

## What It Does

Securities class action complaints are public filings available through PACER/RECAP. The patterns across hundreds of cases — which plaintiff firms target which industries, which judges resolve cases fastest, how allegation types distribute across sectors — are invisible unless you build a graph. This tool makes that graph.

1. **Seed** — 12 real securities class action cases (2012–2019), pre-loaded with complaint text
2. **Extract** — Claude reads each complaint and returns structured JSON: allegation type, harm theory, key allegations, named defendant officers, and class period
3. **Graph** — NetworkX DiGraph links plaintiff firms → defendant companies → judges; edge color encodes allegation type
4. **Patterns** — aggregated views: firm × industry matrix, judge resolution statistics, allegation type distribution, $-recovery tracking
5. **Live mode** — CourtListener RECAP search returns additional case metadata; with an API key, full docket text is available for richer extraction

---

## The 12 Seed Cases

| Case | Allegation | Recovery | Resolution |
|------|-----------|---------|------------|
| In re Valeant Pharmaceuticals | Accounting fraud | $1.21B | Settlement |
| Halliburton Co. v. Erica P. John Fund | Disclosure failure | $100M | Settlement |
| In re Lumber Liquidators | Product safety | $36M | Settlement |
| Dura Pharmaceuticals v. Broudo | Forward-looking statements | N/A | Remand |
| Tellabs, Inc. v. Makor Issues | Disclosure failure | $3.5M | Settlement |
| In re Tesla Motors (2018) | Market manipulation | $0 | Jury verdict for defendant (Feb 2023) |
| Matrixx Initiatives v. Siracusano | Product safety disclosure | $12M | Settlement |
| Omnicare v. Laborers District Council | Forward-looking statements | $10.5M | Settlement |
| Amgen Inc. v. CT Retirement Plans | Revenue recognition | $95M | Settlement |
| Erica P. John Fund v. Halliburton | Disclosure failure | $7.5M | Settlement |
| Merck & Co. v. Reynolds | Accounting fraud | $830M | Settlement |
| Basic Inc. v. Levinson | Disclosure failure | $45M | Settlement |

$2.4B+ approximate total tracked recovery. Spans 5 allegation types, 6 plaintiff firms, 9 judges, 5 industry sectors.

---

## Allegation Taxonomy

| Type | Description |
|------|-------------|
| `accounting_fraud` | Materially misstated financial statements |
| `disclosure_failure` | Omission of material information required by SEC rules |
| `insider_trading` | Trading on material non-public information |
| `forward_looking_statements` | False/misleading projections or guidance |
| `revenue_recognition` | Improper revenue timing or classification |
| `market_manipulation` | Coordinated activity to artificially move price |
| `product_safety_disclosure` | Failure to disclose known product safety risks |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python |
| AI | Claude Haiku (complaint text → structured allegation JSON) |
| Live case data | CourtListener RECAP API (free, no auth for metadata; API key for full text) |
| Graph | NetworkX 3.3 (DiGraph) |
| Visualization | Plotly (interactive network graph via CDN) |
| Database | SQLite + SQLAlchemy 2.0 |
| Frontend | Jinja2 templates + vanilla CSS |
| Deploy | Render (DEMO_MODE=True) |

---

## Quick Start

```bash
git clone https://github.com/JakPot42/litigation-network.git
cd litigation-network
cp .env.example .env          # add ANTHROPIC_API_KEY=sk-ant-...
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\uvicorn main:app --reload
```

Open http://localhost:8000

To enable live CourtListener docket text (optional):

```
COURTLISTENER_API_KEY=your-key   # free at courtlistener.com
```

---

## Architecture

```
courtlistener_client.py  CourtListener RECAP search, docket fetch, document text retrieval
complaint_extractor.py   Claude Haiku: complaint text → {allegation_type, harm_theory, key_allegations, defendant_officers, class_period}
graph_builder.py         NetworkX DiGraph: plaintiff firm → defendant company → judge; edge color = allegation type
models.py                SQLAlchemy ORM (Case, Party, Judge, AllegationExtraction, GraphEdge)
seed_data.py             12 real cases with pre-extracted allegations and resolution data
main.py                  FastAPI routes (graph view, patterns, case detail, search), Jinja rendering
```

---

## Key Architecture Decisions

**Why graph, not table:**
Tabular case data is what PACER already provides. The value here is the relational structure — which plaintiff firms co-appear against the same defendants, which judges see disproportionate volumes of a specific allegation type, whether certain industries cluster by allegation. A graph makes these patterns visible; a table buries them.

**Why Claude extracts, deterministic logic aggregates:**
Claude's job is to read complaint text and extract structured facts (allegation type, harm theory, class period). NetworkX's job is to build and traverse the graph. Plotly's job is to render it. Claude never makes legal judgments — it classifies into a fixed taxonomy.

**Why CourtListener over PACER:**
PACER charges per page. CourtListener's RECAP archive has millions of public documents available for free. The live search mode uses CourtListener's free RECAP API; the API key unlocks full document text for richer Claude extraction.

---

## Honest Limitations

- Claude extraction quality depends on complaint text length and specificity — short summaries produce less detailed output than full complaints.
- The allegation taxonomy covers the 7 most common types in securities class actions; unusual or novel theories may be misclassified.
- Recovery amounts in seed data are approximate; some cases have confidential settlement terms.
- Tesla's 2023 jury verdict for the defendant is included as a data point — the tool does not predict outcomes.
- DEMO_MODE=True on Render; live CourtListener search is available locally.

---

## Tests

```bash
venv\Scripts\python.exe -m pytest tests/ -v
# 119 passed
```

Covers: complaint extractor JSON parsing, allegation type validation, NetworkX graph construction (edge count, node types), Plotly data format, CourtListener client mocking, pattern aggregation math, seed data integrity.

---

*Case data sourced from public PACER/RECAP filings via CourtListener. Recovery amounts are approximate. Not for legal research without independent verification.*
