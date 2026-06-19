import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from config import DATABASE_URL


class Base(DeclarativeBase):
    pass


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_name = Column(String(400), nullable=False)
    docket_number = Column(String(40), nullable=False)
    court = Column(String(100), nullable=False)
    date_filed = Column(String(20), nullable=True)
    defendant_company = Column(String(200), nullable=False)
    industry_sector = Column(String(50), nullable=False, default="Other")
    plaintiff_law_firm = Column(String(200), nullable=False)
    judge_name = Column(String(200), nullable=True)

    # Claude-extracted fields
    allegation_type = Column(String(50), nullable=False)
    harm_theory = Column(Text, nullable=False)
    key_allegations_json = Column(Text, nullable=False, default="[]")
    defendant_officers_json = Column(Text, nullable=False, default="[]")
    class_period_start = Column(String(20), nullable=True)
    class_period_end = Column(String(20), nullable=True)

    # Case outcome
    status = Column(String(20), nullable=False, default="filed")  # filed, settled, dismissed, ongoing
    settlement_amount_usd = Column(Float, nullable=True)
    settlement_date = Column(String(20), nullable=True)
    days_to_resolution = Column(Integer, nullable=True)

    # Source
    courtlistener_url = Column(String(500), nullable=True)
    summary_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def get_key_allegations(self) -> list[str]:
        return json.loads(self.key_allegations_json)

    def get_defendant_officers(self) -> list[str]:
        return json.loads(self.defendant_officers_json)

    def class_period_str(self) -> str | None:
        if self.class_period_start and self.class_period_end:
            return f"{self.class_period_start} — {self.class_period_end}"
        return None

    def settlement_str(self) -> str | None:
        if self.settlement_amount_usd:
            amt = self.settlement_amount_usd
            if amt >= 1_000_000_000:
                return f"${amt / 1_000_000_000:.2f}B"
            return f"${amt / 1_000_000:.1f}M"
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "case_name": self.case_name,
            "docket_number": self.docket_number,
            "court": self.court,
            "date_filed": self.date_filed,
            "defendant_company": self.defendant_company,
            "industry_sector": self.industry_sector,
            "plaintiff_law_firm": self.plaintiff_law_firm,
            "judge_name": self.judge_name,
            "allegation_type": self.allegation_type,
            "harm_theory": self.harm_theory,
            "key_allegations": self.get_key_allegations(),
            "defendant_officers": self.get_defendant_officers(),
            "class_period_start": self.class_period_start,
            "class_period_end": self.class_period_end,
            "status": self.status,
            "settlement_amount_usd": self.settlement_amount_usd,
            "settlement_date": self.settlement_date,
            "days_to_resolution": self.days_to_resolution,
            "courtlistener_url": self.courtlistener_url,
        }


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    return _engine


def init_db():
    Base.metadata.create_all(get_engine())


def get_db():
    with Session(get_engine()) as session:
        yield session
