import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() in ("1", "true", "yes")
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./litigation.db")
APP_TITLE = "Securities Litigation Network"

COURTLISTENER_BASE = "https://www.courtlistener.com"
COURTLISTENER_API = f"{COURTLISTENER_BASE}/api/rest/v4"
COURTLISTENER_API_KEY = os.getenv("COURTLISTENER_API_KEY", "")
COURTLISTENER_TIMEOUT = 15

ALLEGATION_TYPES = [
    "accounting_fraud",
    "disclosure_failure",
    "insider_trading",
    "forward_looking_statements",
    "revenue_recognition",
    "market_manipulation",
    "product_safety_disclosure",
]

ALLEGATION_LABELS = {
    "accounting_fraud": "Accounting Fraud",
    "disclosure_failure": "Disclosure Failure",
    "insider_trading": "Insider Trading",
    "forward_looking_statements": "Forward-Looking Statements",
    "revenue_recognition": "Revenue Recognition",
    "market_manipulation": "Market Manipulation",
    "product_safety_disclosure": "Product Safety Disclosure",
}

ALLEGATION_COLORS = {
    "accounting_fraud": "#dc3545",
    "disclosure_failure": "#fd7e14",
    "insider_trading": "#6610f2",
    "forward_looking_statements": "#0d6efd",
    "revenue_recognition": "#20c997",
    "market_manipulation": "#ffc107",
    "product_safety_disclosure": "#198754",
}

SECTOR_COLORS = {
    "Technology": "#0d6efd",
    "Finance": "#fd7e14",
    "Healthcare": "#198754",
    "Energy": "#ffc107",
    "Consumer": "#dc3545",
    "Retail": "#6f42c1",
    "Other": "#6c757d",
}
