"""Tests for complaint_extractor.py — Claude extraction and DEMO_MODE behavior."""
import os
import pytest

# Force DEMO_MODE for all tests
os.environ["DEMO_MODE"] = "True"

from complaint_extractor import (
    extract_complaint,
    _DEMO_EXTRACTIONS,
    _default_extraction,
    _error_extraction,
)
from config import ALLEGATION_TYPES


# ---------------------------------------------------------------------------
# _DEMO_EXTRACTIONS schema validation
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {
    "allegation_type", "harm_theory", "key_allegations",
    "defendant_officers", "class_period_start", "class_period_end", "industry_sector",
}


@pytest.mark.parametrize("case_name", list(_DEMO_EXTRACTIONS.keys()))
def test_demo_extraction_has_required_fields(case_name):
    extraction = _DEMO_EXTRACTIONS[case_name]
    for field in REQUIRED_FIELDS:
        assert field in extraction, f"{case_name} missing field: {field}"


@pytest.mark.parametrize("case_name", list(_DEMO_EXTRACTIONS.keys()))
def test_demo_extraction_allegation_type_valid(case_name):
    extraction = _DEMO_EXTRACTIONS[case_name]
    assert extraction["allegation_type"] in ALLEGATION_TYPES


@pytest.mark.parametrize("case_name", list(_DEMO_EXTRACTIONS.keys()))
def test_demo_extraction_harm_theory_nonempty(case_name):
    extraction = _DEMO_EXTRACTIONS[case_name]
    assert len(extraction["harm_theory"]) > 50


@pytest.mark.parametrize("case_name", list(_DEMO_EXTRACTIONS.keys()))
def test_demo_extraction_key_allegations_list(case_name):
    extraction = _DEMO_EXTRACTIONS[case_name]
    assert isinstance(extraction["key_allegations"], list)
    assert len(extraction["key_allegations"]) >= 3


@pytest.mark.parametrize("case_name", list(_DEMO_EXTRACTIONS.keys()))
def test_demo_extraction_defendant_officers_list(case_name):
    extraction = _DEMO_EXTRACTIONS[case_name]
    assert isinstance(extraction["defendant_officers"], list)


@pytest.mark.parametrize("case_name", list(_DEMO_EXTRACTIONS.keys()))
def test_demo_extraction_industry_sector_valid(case_name):
    valid_sectors = {"Technology", "Finance", "Healthcare", "Energy", "Consumer", "Retail", "Other"}
    extraction = _DEMO_EXTRACTIONS[case_name]
    assert extraction["industry_sector"] in valid_sectors


# ---------------------------------------------------------------------------
# DEMO_MODE behavior of extract_complaint()
# ---------------------------------------------------------------------------

def test_extract_complaint_demo_mode_returns_prebaked():
    case_name = "In re Tesla, Inc. Securities Litigation"
    result = extract_complaint("some text", case_name)
    assert result["allegation_type"] == "disclosure_failure"
    assert "Elon Musk" in result["harm_theory"] or "funding secured" in result["harm_theory"]


def test_extract_complaint_demo_mode_unknown_case_returns_default():
    result = extract_complaint("some text", "Unknown v. Nobody Inc.")
    assert result["allegation_type"] == "disclosure_failure"
    assert "Unknown v. Nobody Inc." in result["harm_theory"]


def test_extract_complaint_tesla_class_period():
    result = extract_complaint("", "In re Tesla, Inc. Securities Litigation")
    assert result["class_period_start"] == "2018-08-07"
    assert result["class_period_end"] == "2018-08-17"


def test_extract_complaint_boeing_allegation():
    result = extract_complaint("", "In re Boeing Co. Securities Litigation")
    assert result["allegation_type"] == "disclosure_failure"


def test_extract_complaint_luckin_allegation():
    result = extract_complaint("", "In re Luckin Coffee Inc. Securities Litigation")
    assert result["allegation_type"] == "accounting_fraud"


def test_extract_complaint_valeant_allegation():
    result = extract_complaint("", "In re Valeant Pharmaceuticals International Securities Litigation")
    assert result["allegation_type"] == "accounting_fraud"


def test_extract_complaint_snap_allegation():
    result = extract_complaint("", "In re Snap Inc. Securities Litigation")
    assert result["allegation_type"] == "forward_looking_statements"


def test_extract_complaint_kraft_allegation():
    result = extract_complaint("", "In re Kraft Heinz Securities Litigation")
    assert result["allegation_type"] == "revenue_recognition"


def test_extract_complaint_lumber_allegation():
    result = extract_complaint("", "In re Lumber Liquidators Holdings Securities Litigation")
    assert result["allegation_type"] == "product_safety_disclosure"


def test_extract_complaint_zynga_allegation():
    result = extract_complaint("", "In re Zynga Inc. Securities Litigation")
    assert result["allegation_type"] == "forward_looking_statements"


def test_extract_complaint_ge_allegation():
    result = extract_complaint("", "In re General Electric Company Securities Litigation")
    assert result["allegation_type"] == "accounting_fraud"


def test_extract_complaint_facebook_allegation():
    result = extract_complaint("", "In re Facebook, Inc. Securities Litigation")
    assert result["allegation_type"] == "disclosure_failure"


def test_extract_complaint_uber_allegation():
    result = extract_complaint("", "City of Providence v. Uber Technologies, Inc.")
    assert result["allegation_type"] == "disclosure_failure"


def test_extract_complaint_goldman_allegation():
    result = extract_complaint("", "Sjunde AP-Fonden v. Goldman Sachs Group, Inc.")
    assert result["allegation_type"] == "disclosure_failure"


# ---------------------------------------------------------------------------
# Coverage: all 12 demo cases have extractions
# ---------------------------------------------------------------------------

_EXPECTED_CASES = [
    "In re Tesla, Inc. Securities Litigation",
    "In re Facebook, Inc. Securities Litigation",
    "In re Boeing Co. Securities Litigation",
    "In re Luckin Coffee Inc. Securities Litigation",
    "In re Snap Inc. Securities Litigation",
    "City of Providence v. Uber Technologies, Inc.",
    "In re Zynga Inc. Securities Litigation",
    "In re Lumber Liquidators Holdings Securities Litigation",
    "In re Valeant Pharmaceuticals International Securities Litigation",
    "In re Kraft Heinz Securities Litigation",
    "In re General Electric Company Securities Litigation",
    "Sjunde AP-Fonden v. Goldman Sachs Group, Inc.",
]


def test_all_12_cases_have_extractions():
    for case in _EXPECTED_CASES:
        assert case in _DEMO_EXTRACTIONS, f"Missing demo extraction for: {case}"


def test_allegation_types_used_are_valid_subset():
    # The 12 seed cases cover 5 of 7 types (no insider_trading or market_manipulation
    # in this sample — those are valid types available for live ingestion).
    types_used = {v["allegation_type"] for v in _DEMO_EXTRACTIONS.values()}
    assert types_used.issubset(set(ALLEGATION_TYPES))
    assert len(types_used) >= 5


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def test_default_extraction_includes_case_name():
    result = _default_extraction("My Weird Case v. Nobody")
    assert "My Weird Case v. Nobody" in result["harm_theory"]
    assert result["allegation_type"] == "disclosure_failure"


def test_error_extraction_includes_error_msg():
    result = _error_extraction("Some Case", "connection refused")
    assert "connection refused" in result["harm_theory"]
