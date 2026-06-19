import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from config import APP_TITLE, DEMO_MODE, ALLEGATION_LABELS, ALLEGATION_COLORS, SECTOR_COLORS
from models import Complaint, get_db, get_engine, init_db
from graph_builder import (
    build_network_chart,
    build_allegation_chart,
    build_firm_chart,
    compute_patterns,
)
from complaint_extractor import extract_complaint
from courtlistener_client import (
    search_securities_cases,
    CourtListenerError,
    build_courtlistener_url,
)
from seed_data import load_seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with Session(get_engine()) as db:
        load_seed_data(db)
    yield


app = FastAPI(title=APP_TITLE, lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


def _base_ctx(request: Request) -> dict:
    return {
        "request": request,
        "demo_mode": DEMO_MODE,
        "app_title": APP_TITLE,
        "allegation_labels": ALLEGATION_LABELS,
        "allegation_colors": ALLEGATION_COLORS,
    }


def _complaints_as_dicts(complaints: list[Complaint]) -> list[dict]:
    return [c.to_dict() for c in complaints]


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    complaints = db.query(Complaint).order_by(Complaint.date_filed.desc()).all()
    complaint_dicts = _complaints_as_dicts(complaints)

    network_chart = json.dumps(build_network_chart(complaint_dicts))
    allegation_chart = json.dumps(build_allegation_chart(complaint_dicts))

    total_recovery = sum(
        c.settlement_amount_usd for c in complaints
        if c.settlement_amount_usd and c.status == "settled"
    )

    ctx = _base_ctx(request)
    ctx.update({
        "complaints": complaints,
        "total_cases": len(complaints),
        "settled_count": sum(1 for c in complaints if c.status == "settled"),
        "total_recovery_usd": total_recovery,
        "unique_firms": len({c.plaintiff_law_firm for c in complaints}),
        "unique_companies": len({c.defendant_company for c in complaints}),
        "network_chart": network_chart,
        "allegation_chart": allegation_chart,
    })
    return templates.TemplateResponse(request, "index.html", ctx)


@app.get("/complaint/{complaint_id}", response_class=HTMLResponse)
def complaint_detail(complaint_id: int, request: Request, db: Session = Depends(get_db)):
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        return HTMLResponse("<h1>Not found</h1>", status_code=404)
    ctx = _base_ctx(request)
    ctx.update({"complaint": complaint})
    return templates.TemplateResponse(request, "complaint.html", ctx)


@app.get("/patterns", response_class=HTMLResponse)
def patterns(request: Request, db: Session = Depends(get_db)):
    complaints = db.query(Complaint).order_by(Complaint.date_filed.desc()).all()
    complaint_dicts = _complaints_as_dicts(complaints)
    pattern_data = compute_patterns(complaint_dicts)
    firm_chart = json.dumps(build_firm_chart(complaint_dicts))
    allegation_chart = json.dumps(build_allegation_chart(complaint_dicts))
    ctx = _base_ctx(request)
    ctx.update({
        "pattern_data": pattern_data,
        "firm_chart": firm_chart,
        "allegation_chart": allegation_chart,
        "total_cases": len(complaints),
    })
    return templates.TemplateResponse(request, "patterns.html", ctx)


@app.post("/ingest", response_class=RedirectResponse)
def ingest(
    request: Request,
    search_query: str = Form(""),
    docket_number: str = Form(""),
    db: Session = Depends(get_db),
):
    if DEMO_MODE:
        return RedirectResponse(url="/?demo_notice=1", status_code=303)

    search_query = search_query.strip() or "securities class action"
    try:
        results = search_securities_cases(search_query, page_size=5)
    except CourtListenerError as exc:
        return RedirectResponse(url=f"/?error={str(exc)[:120]}", status_code=303)

    added = 0
    for result in results:
        case_name = result.get("case_name", "")
        if not case_name:
            continue

        existing = db.query(Complaint).filter(
            Complaint.docket_number == result.get("docket_number", "")
        ).first()
        if existing:
            continue

        # Build text for Claude from available metadata
        meta_text = (
            f"Case: {case_name}\n"
            f"Court: {result.get('court', '')}\n"
            f"Cause of Action: {result.get('cause', '')}\n"
            f"Date Filed: {result.get('date_filed', '')}\n"
            f"Attorneys: {', '.join(result.get('attorneys', [])[:5])}\n"
            f"Firms: {', '.join(result.get('firms', [])[:5])}\n"
        )

        extraction = extract_complaint(meta_text, case_name)

        firms = result.get("firms") or []
        plaintiff_firm = firms[0] if firms else "Unknown"

        cl_url = build_courtlistener_url(result.get("docket_absolute_url", ""))

        complaint = Complaint(
            case_name=case_name,
            docket_number=result.get("docket_number", ""),
            court=result.get("court", ""),
            date_filed=result.get("date_filed", ""),
            defendant_company=_extract_defendant(case_name),
            industry_sector=extraction.get("industry_sector", "Other"),
            plaintiff_law_firm=plaintiff_firm,
            judge_name=result.get("judge_name") or None,
            allegation_type=extraction.get("allegation_type", "disclosure_failure"),
            harm_theory=extraction.get("harm_theory", ""),
            key_allegations_json=json.dumps(extraction.get("key_allegations", [])),
            defendant_officers_json=json.dumps(extraction.get("defendant_officers", [])),
            class_period_start=extraction.get("class_period_start"),
            class_period_end=extraction.get("class_period_end"),
            status="filed",
            courtlistener_url=cl_url,
            summary_text=meta_text,
        )
        db.add(complaint)
        added += 1

    db.commit()
    return RedirectResponse(url=f"/?added={added}", status_code=303)


@app.get("/api/stats")
def api_stats(db: Session = Depends(get_db)):
    total = db.query(Complaint).count()
    settled = db.query(Complaint).filter(Complaint.status == "settled").count()
    return JSONResponse({
        "status": "ok",
        "total_complaints": total,
        "settled": settled,
        "demo_mode": DEMO_MODE,
    })


def _extract_defendant(case_name: str) -> str:
    """Heuristically extract defendant company name from case name."""
    lower = case_name.lower()
    # "In re X Securities Litigation" → X
    if "in re " in lower and " securities" in lower:
        start = lower.index("in re ") + 6
        end = lower.index(" securities")
        return case_name[start:end].strip()
    # "X v. Y" → Y
    if " v. " in case_name:
        return case_name.split(" v. ")[-1].strip()
    return case_name
